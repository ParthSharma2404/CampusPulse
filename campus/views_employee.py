import os
from datetime import datetime
from bson import ObjectId
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .db import (
    get_users_collection,
    get_departments_collection,
    get_issues_collection,
    get_notifications_collection,
    verify_password
)
from .services import (
    resolve_issue_and_notify,
    save_uploaded_file,
    normalize_building_code
)

def employee_login_required(view_func):
    """Decorator to enforce employee/technician authentication."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('employee_id') or request.session.get('employee_role') != 'employee':
            messages.info(request, "Staff zone. Please sign in with your maintenance employee credentials.")
            return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def employee_login_view(request):
    """Dedicated login view for campus maintenance technicians and staff."""
    if request.session.get('employee_id') and request.session.get('employee_role') == 'employee':
        return redirect('employee_dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, "Please enter your employee ID or email and password.")
            return render(request, 'campus/employee/login.html')

        users = get_users_collection()
        emp_user = users.find_one({
            "$or": [
                {"email": identifier.lower()},
                {"employee_id": identifier.upper()}
            ],
            "role": "employee"
        })

        if not emp_user or not verify_password(password, emp_user.get('password_hash', '')):
            messages.error(request, "Invalid staff credentials. Please check your employee ID and password.")
            return render(request, 'campus/employee/login.html')

        if not emp_user.get('is_active', True):
            messages.error(request, "Your staff account is currently inactive. Contact Facility Operations.")
            return render(request, 'campus/employee/login.html')

        # Clear prior session state
        request.session.flush()

        # Set employee session
        request.session['employee_id'] = str(emp_user['_id'])
        request.session['employee_name'] = emp_user.get('name')
        request.session['employee_code'] = emp_user.get('employee_id')
        request.session['employee_role'] = 'employee'
        request.session['employee_dept_id'] = str(emp_user.get('department_id', ''))

        messages.success(request, f"Welcome back, {emp_user.get('name')}! Duty dashboard active.")
        return redirect('employee_dashboard')

    return render(request, 'campus/employee/login.html')


def employee_logout_view(request):
    """Employee sign-out view."""
    request.session.flush()
    messages.info(request, "Signed out of employee operations console.")
    return redirect('employee_login')


@employee_login_required
def employee_dashboard_view(request):
    """Employee operations console: view assigned hostel complaints and fulfill requests."""
    emp_id_str = request.session.get('employee_id')
    emp_id = ObjectId(emp_id_str)

    users_coll = get_users_collection()
    issues_coll = get_issues_collection()
    dept_coll = get_departments_collection()

    employee = users_coll.find_one({"_id": emp_id, "role": "employee"})
    if not employee:
        messages.error(request, "Employee profile not found.")
        return redirect('employee_login')

    department = None
    if employee.get('department_id'):
        department = dept_coll.find_one({"_id": employee['department_id']})

    assigned_buildings = employee.get('assigned_buildings', [])

    # Filter parameter: all, assigned, in_progress, resolved
    status_filter = request.GET.get('status', 'ACTIVE')
    building_filter = request.GET.get('building', '').strip()

    # Query: issues directly assigned to this employee OR in employee's assigned buildings & department
    base_query = {
        "$or": [
            {"assigned_to.employee_id": emp_id},
            {
                "department_id": employee.get('department_id'),
                "location.building_or_block": {"$in": assigned_buildings}
            }
        ]
    }

    if status_filter == 'ACTIVE':
        base_query["status"] = {"$in": ["ASSIGNED", "REPORTED", "IN_PROGRESS"]}
    elif status_filter in ['ASSIGNED', 'IN_PROGRESS', 'RESOLVED']:
        base_query["status"] = status_filter

    if building_filter:
        base_query["location.building_or_block"] = building_filter

    my_issues = list(issues_coll.find(base_query).sort("updated_at", -1))

    # Decorate issues
    for issue in my_issues:
        issue['id'] = str(issue['_id'])
        if issue.get('created_at'):
            issue['created_at_fmt'] = issue['created_at'].strftime("%b %d, %I:%M %p")
        if issue.get('resolved_at'):
            issue['resolved_at_fmt'] = issue['resolved_at'].strftime("%b %d, %I:%M %p")

    # Metrics
    count_assigned = issues_coll.count_documents({
        "$or": [{"assigned_to.employee_id": emp_id}, {"location.building_or_block": {"$in": assigned_buildings}}],
        "status": {"$in": ["ASSIGNED", "REPORTED"]}
    })
    count_in_progress = issues_coll.count_documents({
        "$or": [{"assigned_to.employee_id": emp_id}, {"location.building_or_block": {"$in": assigned_buildings}}],
        "status": "IN_PROGRESS"
    })
    count_resolved = issues_coll.count_documents({
        "$or": [{"assigned_to.employee_id": emp_id}, {"location.building_or_block": {"$in": assigned_buildings}}],
        "status": "RESOLVED"
    })

    return render(request, 'campus/employee/dashboard.html', {
        "employee": employee,
        "department": department,
        "assigned_buildings": assigned_buildings,
        "issues": my_issues,
        "status_filter": status_filter,
        "building_filter": building_filter,
        "count_assigned": count_assigned,
        "count_in_progress": count_in_progress,
        "count_resolved": count_resolved,
    })


@employee_login_required
@require_POST
def employee_start_work_view(request, issue_id):
    """Employee marks an assigned complaint as IN_PROGRESS."""
    emp_id = ObjectId(request.session.get('employee_id'))
    issues_coll = get_issues_collection()

    issue = issues_coll.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        messages.error(request, "Ticket not found.")
        return redirect('employee_dashboard')

    issues_coll.update_one(
        {"_id": ObjectId(issue_id)},
        {
            "$set": {
                "status": "IN_PROGRESS",
                "technician_work_started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    messages.success(request, f"Work marked IN PROGRESS for Ticket #{issue.get('ticket_id')}.")
    return redirect('employee_dashboard')


@employee_login_required
@require_POST
def employee_resolve_issue_view(request, issue_id):
    """Employee completes repair, submits notes, and broadcasts instant resolution to students."""
    emp_id = ObjectId(request.session.get('employee_id'))
    resolution_notes = request.POST.get('resolution_notes', '').strip()

    if not resolution_notes:
        messages.error(request, "Please describe the technician action taken to fulfill this repair.")
        return redirect('employee_dashboard')

    # Handle completion photo if uploaded
    resolution_image = ""
    uploaded_image = request.FILES.get('resolution_photo')
    if uploaded_image:
        img_path = save_uploaded_file(uploaded_image, subfolder="resolutions")
        if img_path:
            resolution_image = img_path

    success, msg = resolve_issue_and_notify(
        issue_id=ObjectId(issue_id),
        admin_id=emp_id,
        resolution_notes=resolution_notes,
        resolution_image=resolution_image
    )

    if success:
        messages.success(request, "Defect repair completed and broadcasted to student in real time.")
    else:
        messages.error(request, msg)

    return redirect('employee_dashboard')
