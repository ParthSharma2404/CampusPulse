import os
from datetime import datetime
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .db import (
    get_users_collection,
    get_departments_collection,
    get_issues_collection,
    get_notifications_collection,
    get_buildings_collection,
    hash_password,
    verify_password
)
from .services import (
    resolve_issue_and_notify,
    save_uploaded_file
)

def admin_login_required(view_func):
    """Decorator to enforce admin authentication."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id') or request.session.get('admin_role') != 'admin':
            messages.info(request, "Restricted administrative zone. Please log in with admin credentials.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_login_view(request):
    """Stealth admin login route at /admin/login."""
    if request.session.get('admin_id') and request.session.get('admin_role') == 'admin':
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Please enter admin email and password.")
            return render(request, 'campus/admin/login.html')

        users = get_users_collection()
        admin_user = users.find_one({"email": email, "role": "admin"})

        if not admin_user or not verify_password(password, admin_user.get('password_hash', '')):
            messages.error(request, "Invalid administrator credentials.")
            return render(request, 'campus/admin/login.html')

        # Clear any prior session state
        request.session.flush()
        # Set admin session
        request.session['admin_id'] = str(admin_user['_id'])
        request.session['admin_name'] = admin_user.get('name', 'Admin')
        request.session['admin_role'] = 'admin'

        messages.success(request, f"Welcome to the Administrative Command Center, {admin_user.get('name')}.")
        return redirect('admin_dashboard')

    return render(request, 'campus/admin/login.html')


def admin_logout_view(request):
    """Admin logout view."""
    if 'admin_id' in request.session:
        del request.session['admin_id']
    if 'admin_name' in request.session:
        del request.session['admin_name']
    if 'admin_role' in request.session:
        del request.session['admin_role']
    messages.info(request, "Logged out of administrative console.")
    return redirect('admin_login')


@admin_login_required
def admin_dashboard_view(request):
    issues_coll = get_issues_collection()
    dept_coll = get_departments_collection()
    users_coll = get_users_collection()

    dept_filter = request.GET.get('dept', '')
    status_filter = request.GET.get('status', 'REPORTED')  # Default to active REPORTED
    search_query = request.GET.get('q', '').strip()

    # Build query
    query = {}
    if status_filter in ['REPORTED', 'RESOLVED']:
        query['status'] = status_filter

    if dept_filter:
        try:
            query['department_id'] = ObjectId(dept_filter)
        except Exception:
            pass

    if search_query:
        query['$or'] = [
            {"ticket_id": {"$regex": search_query, "$options": "i"}},
            {"title": {"$regex": search_query, "$options": "i"}},
            {"location.building_or_block": {"$regex": search_query, "$options": "i"}},
            {"location.room_or_area": {"$regex": search_query, "$options": "i"}}
        ]

    # Fetch departments
    departments = list(dept_coll.find().sort("name", 1))
    dept_map = {}
    for d in departments:
        d['id'] = str(d['_id'])
        dept_map[d['id']] = d

    # Fetch issues
    issues = list(issues_coll.find(query).sort([("priority", -1), ("report_count", -1), ("created_at", -1)]))

    # Collect user IDs for batch lookup
    user_ids = set()
    for issue in issues:
        issue['id'] = str(issue['_id'])
        if issue.get("reported_by"):
            user_ids.add(issue["reported_by"])
        for cid in issue.get("co_affected_students", []):
            user_ids.add(cid)

    users_map = {str(u["_id"]): u for u in users_coll.find({"_id": {"$in": list(user_ids)}})}

    # Decorate issues
    for issue in issues:
        dept_id_str = str(issue.get("department_id"))
        issue["department"] = dept_map.get(dept_id_str, {
            "name": "General Maintenance",
            "color_tag": "#6B7280"
        })
        rep_id_str = str(issue.get("reported_by"))
        issue["reporter"] = users_map.get(rep_id_str, {
            "name": "Student",
            "registration_number": "N/A",
            "phone": "N/A"
        })
        # Affected students list
        affected_list = []
        for cid in issue.get("co_affected_students", []):
            student_obj = users_map.get(str(cid))
            if student_obj:
                affected_list.append(student_obj)
        issue["co_affected_users"] = affected_list

        if issue.get("created_at"):
            issue["created_at_fmt"] = issue["created_at"].strftime("%b %d, %Y • %I:%M %p")
        if issue.get("resolved_at"):
            issue["resolved_at_fmt"] = issue["resolved_at"].strftime("%b %d, %Y • %I:%M %p")

    # Global KPI metrics
    total_active_hotspots = issues_coll.count_documents({"status": "REPORTED"})
    total_resolved = issues_coll.count_documents({"status": "RESOLVED"})
    urgent_count = issues_coll.count_documents({"status": "REPORTED", "priority": {"$in": ["HIGH", "URGENT"]}})

    # Calculate total student reports impacted
    pipeline = [
        {"$match": {"status": "REPORTED"}},
        {"$group": {"_id": None, "total_impact": {"$sum": "$report_count"}}}
    ]
    agg_res = list(issues_coll.aggregate(pipeline))
    total_students_impacted = agg_res[0]["total_impact"] if agg_res else 0

    # Top Hotspots (multiple reports at same location)
    hotspots = list(issues_coll.find({
        "status": "REPORTED",
        "report_count": {"$gte": 2}
    }).sort("report_count", -1).limit(5))

    for h in hotspots:
        h['id'] = str(h['_id'])
        dept_id_str = str(h.get("department_id"))
        h["department"] = dept_map.get(dept_id_str, {"name": "Maintenance", "color_tag": "#6B7280"})

    context = {
        "issues": issues,
        "departments": departments,
        "selected_dept": dept_filter,
        "status_filter": status_filter,
        "search_query": search_query,
        "total_active_hotspots": total_active_hotspots,
        "total_resolved": total_resolved,
        "urgent_count": urgent_count,
        "total_students_impacted": total_students_impacted,
        "hotspots": hotspots,
        "admin_name": request.session.get('admin_name', 'Administrator')
    }


    return render(request, 'campus/admin/dashboard.html', context)


@admin_login_required
@require_POST
def admin_resolve_issue_view(request, issue_id):
    """Handles defect resolution and triggers real-time broadcast to all affected students."""
    try:
        issue_obj_id = ObjectId(issue_id)
    except Exception:
        messages.error(request, "Invalid issue ID.")
        return redirect('admin_dashboard')

    admin_id = ObjectId(request.session.get('admin_id'))
    resolution_notes = request.POST.get('resolution_notes', '').strip()
    if not resolution_notes:
        messages.error(request, "Please provide resolution remarks explaining what was fixed.")
        return redirect('admin_dashboard')

    # Optional resolution proof photo
    resolution_image = ""
    uploaded_photo = request.FILES.get('resolution_photo')
    if uploaded_photo:
        resolution_image = save_uploaded_file(uploaded_photo, subfolder="resolutions") or ""

    success, msg = resolve_issue_and_notify(
        issue_id=issue_obj_id,
        admin_id=admin_id,
        resolution_notes=resolution_notes,
        resolution_image=resolution_image
    )

    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect('admin_dashboard')


@admin_login_required
def admin_departments_view(request):
    """Dynamic department management: Admin can add new departments directly through their dashboard."""
    dept_coll = get_departments_collection()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip().upper()
            description = request.POST.get('description', '').strip()
            contact_person = request.POST.get('contact_person', '').strip()
            contact_email = request.POST.get('contact_email', '').strip().lower()
            contact_phone = request.POST.get('contact_phone', '').strip()
            color_tag = request.POST.get('color_tag', '#4F46E5').strip()
            sla_hours = int(request.POST.get('sla_resolution_hours', 24))

            if not name or not code:
                messages.error(request, "Department Name and Code are required.")
                return redirect('admin_departments')

            if dept_coll.find_one({"code": code}):
                messages.error(request, f"Department code '{code}' already exists.")
                return redirect('admin_departments')

            dept_doc = {
                "name": name,
                "code": code,
                "description": description,
                "contact_person": contact_person,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "color_tag": color_tag,
                "sla_resolution_hours": sla_hours,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            dept_coll.insert_one(dept_doc)
            messages.success(request, f"Department '{name}' has been created successfully!")
            return redirect('admin_departments')

        elif action == 'toggle_status':
            dept_id = request.POST.get('dept_id')
            if dept_id:
                dept = dept_coll.find_one({"_id": ObjectId(dept_id)})
                if dept:
                    new_status = not dept.get('is_active', True)
                    dept_coll.update_one({"_id": ObjectId(dept_id)}, {"$set": {"is_active": new_status}})
                    status_str = "Activated" if new_status else "Deactivated"
                    messages.success(request, f"Department '{dept.get('name')}' {status_str}.")
            return redirect('admin_departments')

    departments = list(dept_coll.find().sort("name", 1))
    for d in departments:
        d['id'] = str(d['_id'])
    return render(request, 'campus/admin/departments.html', {
        "departments": departments,
        "admin_name": request.session.get('admin_name', 'Administrator')
    })


@admin_login_required
def admin_buildings_view(request):
    """Admin console to manage campus hostels (BH1-BH13, GH1-GH13) and facilities."""
    bldg_coll = get_buildings_collection()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_building':
            code = request.POST.get('code', '').strip().upper()
            name = request.POST.get('name', '').strip()
            bldg_type = request.POST.get('type', 'HOSTEL_BOYS').strip()
            floors_str = request.POST.get('total_floors', '6').strip()
            warden_contact = request.POST.get('warden_contact', '').strip()

            try:
                floors = int(floors_str)
            except ValueError:
                floors = 6

            if not code or not name:
                messages.error(request, "Building code and name are mandatory.")
                return redirect('admin_buildings')

            if bldg_coll.find_one({"code": code}):
                messages.error(request, f"Building with code '{code}' already exists.")
                return redirect('admin_buildings')

            new_bldg = {
                "code": code,
                "name": name,
                "type": bldg_type,
                "total_floors": floors,
                "warden_contact": warden_contact,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            bldg_coll.insert_one(new_bldg)
            messages.success(request, f"Building '{name} ({code})' added to campus registry.")
            return redirect('admin_buildings')

        elif action == 'toggle_status':
            bldg_id = request.POST.get('bldg_id')
            if bldg_id:
                bldg = bldg_coll.find_one({"_id": ObjectId(bldg_id)})
                if bldg:
                    new_status = not bldg.get('is_active', True)
                    bldg_coll.update_one({"_id": ObjectId(bldg_id)}, {"$set": {"is_active": new_status}})
                    status_text = "Activated" if new_status else "Deactivated"
                    messages.success(request, f"Building '{bldg.get('name')}' {status_text}.")
            return redirect('admin_buildings')

    # Fetch buildings sorted by type and code
    buildings = list(bldg_coll.find().sort([("type", 1), ("code", 1)]))
    for b in buildings:
        b['id'] = str(b['_id'])

    total_hostels = sum(1 for b in buildings if b.get('type') in ['HOSTEL_BOYS', 'HOSTEL_GIRLS'])
    total_active = sum(1 for b in buildings if b.get('is_active', True))

    return render(request, 'campus/admin/buildings.html', {
        "buildings": buildings,
        "total_hostels": total_hostels,
        "total_active": total_active,
        "admin_name": request.session.get('admin_name', 'Administrator')
    })


@admin_login_required
def admin_employees_view(request):
    """Admin console to manage operational employees and hostel duty assignments."""
    users_coll = get_users_collection()
    dept_coll = get_departments_collection()
    bldg_coll = get_buildings_collection()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_employee':
            name = request.POST.get('name', '').strip()
            employee_id = request.POST.get('employee_id', '').strip().upper()
            email = request.POST.get('email', '').strip().lower()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '').strip()
            dept_id_str = request.POST.get('department_id', '').strip()
            duty_shift = request.POST.get('duty_shift', 'General Shift (8 AM - 6 PM)').strip()
            assigned_buildings = request.POST.getlist('assigned_buildings')

            if not name or not employee_id or not email or not password or not dept_id_str:
                messages.error(request, "Name, Employee ID, Email, Password, and Department are required.")
                return redirect('admin_employees')

            # Enforce mandatory block/building duty selection
            if not assigned_buildings or len(assigned_buildings) == 0:
                messages.error(request, "Duty block selection is required. Please select at least one hostel or campus building.")
                return redirect('admin_employees')

            if users_coll.find_one({"$or": [{"email": email}, {"employee_id": employee_id}]}):
                messages.error(request, f"An employee with this email or ID '{employee_id}' is already registered.")
                return redirect('admin_employees')

            try:
                dept_obj_id = ObjectId(dept_id_str)
            except Exception:
                messages.error(request, "Invalid department selected.")
                return redirect('admin_employees')

            emp_doc = {
                "name": name,
                "employee_id": employee_id,
                "email": email,
                "phone": phone,
                "password_hash": hash_password(password),
                "role": "employee",
                "department_id": dept_obj_id,
                "assigned_buildings": assigned_buildings,
                "duty_shift": duty_shift,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            users_coll.insert_one(emp_doc)
            messages.success(request, f"Employee '{name}' ({employee_id}) successfully registered with duty on {len(assigned_buildings)} building(s).")
            return redirect('admin_employees')

        elif action == 'toggle_status':
            emp_id = request.POST.get('employee_id')
            if emp_id:
                emp = users_coll.find_one({"_id": ObjectId(emp_id), "role": "employee"})
                if emp:
                    new_status = not emp.get('is_active', True)
                    users_coll.update_one({"_id": ObjectId(emp_id)}, {"$set": {"is_active": new_status}})
                    status_str = "Activated" if new_status else "Deactivated"
                    messages.success(request, f"Staff '{emp.get('name')}' {status_str}.")
            return redirect('admin_employees')

        elif action == 'reassign_duty':
            emp_id = request.POST.get('employee_id')
            new_buildings = request.POST.getlist('assigned_buildings')
            if not new_buildings or len(new_buildings) == 0:
                messages.error(request, "Duty block selection is required. Please select at least one building.")
                return redirect('admin_employees')
            if emp_id:
                users_coll.update_one(
                    {"_id": ObjectId(emp_id), "role": "employee"},
                    {"$set": {"assigned_buildings": new_buildings, "updated_at": datetime.utcnow()}}
                )
                messages.success(request, f"Staff duty updated ({len(new_buildings)} blocks assigned).")
            return redirect('admin_employees')

    # Fetch employees, departments, and active buildings
    employees = list(users_coll.find({"role": "employee"}).sort("name", 1))
    departments = list(dept_coll.find({"is_active": True}).sort("name", 1))
    dept_map = {}
    for d in departments:
        d['id'] = str(d['_id'])
        dept_map[d['id']] = d

    for emp in employees:
        emp['id'] = str(emp['_id'])
        dept_id_str = str(emp.get('department_id', ''))
        emp['department'] = dept_map.get(dept_id_str, {"name": "General Maintenance", "color_tag": "#6B7280"})

    buildings = list(bldg_coll.find({"is_active": True}).sort([("type", 1), ("code", 1)]))
    for b in buildings:
        b['id'] = str(b['_id'])

    total_employees = len(employees)
    active_employees = sum(1 for e in employees if e.get('is_active', True))

    return render(request, 'campus/admin/employees.html', {
        "employees": employees,
        "departments": departments,
        "buildings": buildings,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "admin_name": request.session.get('admin_name', 'Administrator')
    })

