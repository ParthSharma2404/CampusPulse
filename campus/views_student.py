import json
import time
from datetime import datetime
from bson import ObjectId
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .db import (
    get_users_collection,
    get_departments_collection,
    get_issues_collection,
    get_notifications_collection,
    get_buildings_collection,
    hash_password,
    verify_password,
    hub
)
from .services import (
    create_or_cluster_issue,
    save_uploaded_file
)

def student_login_required(view_func):
    """Decorator to protect student views."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.info(request, "Please log in with your student credentials.")
            return redirect('student_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def landing_page_view(request):
    """Public landing page displaying live university defect resolution statistics and features."""
    issues_coll = get_issues_collection()
    dept_coll = get_departments_collection()
    users_coll = get_users_collection()

    total_resolved = issues_coll.count_documents({"status": "RESOLVED"})
    total_departments = dept_coll.count_documents({"is_active": True})
    total_active = issues_coll.count_documents({"status": "REPORTED"})
    total_students = users_coll.count_documents({"role": "student"})

    # Fetch active departments
    departments = list(dept_coll.find({"is_active": True}))
    for d in departments:
        d['id'] = str(d['_id'])

    # Fetch recently resolved issues for social proof with student privacy protection
    raw_recent = list(issues_coll.find({"status": "RESOLVED"}).sort("updated_at", -1).limit(6))
    recent_resolved = []
    for r in raw_recent:
        r['id'] = str(r['_id'])
        loc = r.get('location', {})
        loc_type = str(loc.get('location_type', '')).strip().lower()
        bld = str(loc.get('building_or_block', '')).strip()
        bld_lower = bld.lower()

        # Strict Student Privacy Shield: Anonymize private hostel room coordinates
        if loc_type == 'hostel' or 'hostel' in bld_lower or bld_lower.startswith('bh') or bld_lower.startswith('gh'):
            loc['building_or_block'] = "Student Residential Block"
            loc['room_or_area'] = "Private Suite [Room Number Redacted for Privacy]"
            loc['is_privacy_masked'] = True
        else:
            loc['is_privacy_masked'] = False

        recent_resolved.append(r)
        if len(recent_resolved) >= 4:
            break

    return render(request, 'campus/landing.html', {
        "total_resolved": total_resolved,
        "total_departments": total_departments,
        "total_active": total_active,
        "total_students": total_students,
        "departments": departments,
        "recent_resolved": recent_resolved,
    })


def student_register_view(request):

    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        reg_no = request.POST.get('registration_number', '').strip().upper()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        hostel_block = request.POST.get('default_hostel_block', '').strip()
        room_number = request.POST.get('default_room_number', '').strip()

        # Validation
        if not name or not reg_no or not email or not phone or not password:
            messages.error(request, "Please fill in all mandatory fields.")
            return render(request, 'campus/student/register.html', request.POST)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'campus/student/register.html', request.POST)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'campus/student/register.html', request.POST)

        users = get_users_collection()

        # Check existing registration number
        if users.find_one({"registration_number": reg_no}):
            messages.error(request, f"Registration number '{reg_no}' is already registered.")
            return render(request, 'campus/student/register.html', request.POST)

        # Check existing email
        if users.find_one({"email": email}):
            messages.error(request, f"Email '{email}' is already in use.")
            return render(request, 'campus/student/register.html', request.POST)

        # Create user
        new_student = {
            "name": name,
            "registration_number": reg_no,
            "email": email,
            "phone": phone,
            "password_hash": hash_password(password),
            "role": "student",
            "default_hostel_block": hostel_block,
            "default_room_number": room_number,
            "created_at": datetime.utcnow()
        }

        result = users.insert_one(new_student)
        request.session['student_id'] = str(result.inserted_id)
        request.session['student_name'] = name
        request.session['student_reg_no'] = reg_no

        messages.success(request, f"Welcome to CampusPulse, {name}! Your account has been created.")
        return redirect('student_dashboard')

    return render(request, 'campus/student/register.html')


def student_login_view(request):
    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, "Please enter your registration number/email and password.")
            return render(request, 'campus/student/login.html')

        users = get_users_collection()
        # Find by registration number or email
        user = users.find_one({
            "$or": [
                {"registration_number": identifier.upper()},
                {"email": identifier.lower()}
            ],
            "role": "student"
        })

        if not user or not verify_password(password, user.get('password_hash', '')):
            messages.error(request, "Invalid student credentials. Please check your registration number and password.")
            return render(request, 'campus/student/login.html')

        # Clear any prior session state
        request.session.flush()
        # Set session
        request.session['student_id'] = str(user['_id'])
        request.session['student_name'] = user.get('name')
        request.session['student_reg_no'] = user.get('registration_number')

        messages.success(request, f"Welcome back, {user.get('name')}!")
        return redirect('student_dashboard')

    return render(request, 'campus/student/login.html')


def student_logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('student_login')


@student_login_required
def student_dashboard_view(request):
    student_id_str = request.session.get('student_id')
    student_id = ObjectId(student_id_str)

    users = get_users_collection()
    issues_coll = get_issues_collection()
    dept_coll = get_departments_collection()
    notif_coll = get_notifications_collection()

    student = users.find_one({"_id": student_id})
    if not student:
        request.session.flush()
        return redirect('student_login')

    # Query all issues where student is primary reporter OR in co_affected_students
    query = {
        "$or": [
            {"reported_by": student_id},
            {"co_affected_students": student_id}
        ]
    }

    all_student_issues = list(issues_coll.find(query).sort("updated_at", -1))

    # Metric counts
    total_queries = len(all_student_issues)
    pending_queries = sum(1 for issue in all_student_issues if issue.get("status") == "REPORTED")
    fulfilled_queries = sum(1 for issue in all_student_issues if issue.get("status") == "RESOLVED")

    # Fetch departments map for quick lookup
    dept_map = {}
    for d in dept_coll.find():
        d['id'] = str(d['_id'])
        dept_map[d['id']] = d

    # Decorate issues with department details and string id
    for issue in all_student_issues:
        issue['id'] = str(issue['_id'])
        dept_id_str = str(issue.get("department_id"))
        issue["department"] = dept_map.get(dept_id_str, {
            "name": "General Maintenance",
            "color_tag": "#6B7280"
        })
        issue["is_primary_reporter"] = (issue.get("reported_by") == student_id)
        # Formatted dates
        if issue.get("created_at"):
            issue["created_at_fmt"] = issue["created_at"].strftime("%b %d, %Y • %I:%M %p")
        if issue.get("resolved_at"):
            issue["resolved_at_fmt"] = issue["resolved_at"].strftime("%b %d, %Y • %I:%M %p")

    # Fetch student notifications
    recent_notifications = list(notif_coll.find({"recipient_id": student_id}).sort("created_at", -1).limit(15))
    unread_notifs_count = notif_coll.count_documents({"recipient_id": student_id, "is_read": False})

    for notif in recent_notifications:
        notif['id'] = str(notif['_id'])
        if notif.get("created_at"):
            notif["created_at_fmt"] = notif["created_at"].strftime("%b %d, %I:%M %p")

    context = {
        "student": student,
        "total_queries": total_queries,
        "pending_queries": pending_queries,
        "fulfilled_queries": fulfilled_queries,
        "issues": all_student_issues,
        "notifications": recent_notifications,
        "unread_notifs_count": unread_notifs_count,
    }

    return render(request, 'campus/student/dashboard.html', context)


@student_login_required
def report_issue_view(request):
    student_id_str = request.session.get('student_id')
    student_id = ObjectId(student_id_str)

    dept_coll = get_departments_collection()
    users_coll = get_users_collection()
    student = users_coll.find_one({"_id": student_id})

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        dept_id_str = request.POST.get('department_id', '').strip()
        location_type = request.POST.get('location_type', 'Classroom')
        other_location_detail = request.POST.get('other_location_detail', '').strip()
        building = request.POST.get('building_or_block', '').strip()
        floor = request.POST.get('floor', '').strip()
        room = request.POST.get('room_or_area', '').strip()
        description = request.POST.get('description', '').strip()

        # Validate mandatory fields
        if not title or not dept_id_str or not building or not room or not description:
            messages.error(request, "Please fill in all mandatory defect details.")
            departments = list(dept_coll.find({"is_active": True}))
            for d in departments:
                d['id'] = str(d['_id'])
            return render(request, 'campus/student/report_issue.html', {
                "departments": departments,
                "student": student,
                "form_data": request.POST
            })

        try:
            department_obj_id = ObjectId(dept_id_str)
        except Exception:
            messages.error(request, "Invalid department selected.")
            return redirect('report_issue')

        # Handle Image Upload / Camera Snap
        image_paths = []
        uploaded_image = request.FILES.get('defect_photo')
        if uploaded_image:
            img_path = save_uploaded_file(uploaded_image, subfolder="issues")
            if img_path:
                image_paths.append(img_path)

        # Call smart clustering service
        issue_doc, is_new, feedback_msg = create_or_cluster_issue(
            student_id=student_id,
            title=title,
            description=description,
            department_id=department_obj_id,
            location_type=location_type,
            other_location_detail=other_location_detail,
            building=building,
            floor=floor,
            room=room,
            image_paths=image_paths
        )

        if is_new:
            messages.success(request, f"Defect reported! Ticket #{issue_doc.get('ticket_id')} has been created.")
        else:
            messages.info(request, feedback_msg)

        return redirect('student_dashboard')

    # GET request
    departments = list(dept_coll.find({"is_active": True}))
    for d in departments:
        d['id'] = str(d['_id'])
    buildings = list(get_buildings_collection().find({"is_active": True}).sort([("type", 1), ("code", 1)]))
    return render(request, 'campus/student/report_issue.html', {
        "departments": departments,
        "buildings": buildings,
        "student": student
    })



@student_login_required
def notification_stream_view(request):
    """
    Real-Time Server-Sent Events (SSE) endpoint.
    Maintains a persistent HTTP connection to stream resolution updates to the student's browser.
    """
    student_id_str = request.session.get('student_id')
    user_queue = hub.subscribe(student_id_str)

    def event_stream():
        try:
            # Yield initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Real-time alert stream active'})}\n\n"
            while True:
                try:
                    # Wait for notification event with timeout for heartbeat
                    data = user_queue.get(timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except Exception:
                    # Send keep-alive heartbeat comment
                    yield ": ping\n\n"
        finally:
            hub.unsubscribe(student_id_str, user_queue)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@student_login_required
@require_POST
def mark_all_notifications_read_view(request):
    student_id_str = request.session.get('student_id')
    student_id = ObjectId(student_id_str)
    notif_coll = get_notifications_collection()
    notif_coll.update_many({"recipient_id": student_id, "is_read": False}, {"$set": {"is_read": True}})
    return JsonResponse({"status": "ok"})
