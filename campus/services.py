import os
import uuid
from datetime import datetime
from bson import ObjectId
from django.conf import settings
from .db import (
    get_users_collection,
    get_departments_collection,
    get_issues_collection,
    get_notifications_collection,
    hub
)

def generate_ticket_id():
    """Generates a human-friendly ticket ID: CP-YEAR-XXXX."""
    year = datetime.utcnow().year
    random_hex = uuid.uuid4().hex[:6].upper()
    return f"CP-{year}-{random_hex}"

def normalize_location_key(building: str, floor: str, room: str) -> str:
    """Normalizes location parts to cluster identical locations."""
    b = (building or '').strip().lower()
    f = (floor or '').strip().lower()
    r = (room or '').strip().lower()
    return f"{b}__{f}__{r}"

def calculate_priority_from_count(count: int) -> str:
    """Automatically calculates priority based on number of duplicate reports."""
    if count >= 5:
        return 'URGENT'
    elif count >= 3:
        return 'HIGH'
    elif count >= 2:
        return 'MEDIUM'
    return 'LOW'

import re

def normalize_building_code(building_str: str) -> list:
    """Returns canonical building codes for fuzzy matching (e.g. 'BH13', 'Boys Hostel 13' -> ['BH13', 'BOYS HOSTEL 13'])."""
    b = (building_str or '').strip().upper()
    variants = [b]
    # Check BH pattern: BH13, BH-13, BOYS HOSTEL 13, BH 13
    bh_match = re.search(r'\b(?:BH|BOYS HOSTEL)[\s\-]?(\d{1,2})\b', b)
    if bh_match:
        num = bh_match.group(1)
        variants.extend([f"BH{num}", f"BOYS HOSTEL {num}"])
    # Check GH pattern: GH13, GH-13, GIRLS HOSTEL 13, GH 13
    gh_match = re.search(r'\b(?:GH|GIRLS HOSTEL)[\s\-]?(\d{1,2})\b', b)
    if gh_match:
        num = gh_match.group(1)
        variants.extend([f"GH{num}", f"GIRLS HOSTEL {num}"])
    return list(set(variants))

def find_on_duty_employee(building: str, department_id: ObjectId):
    """
    Finds active operational technician/employee on duty for the given building and department.
    """
    users = get_users_collection()
    variants = normalize_building_code(building)
    
    # 1. Exact or regex match in assigned_buildings
    for v in variants:
        emp = users.find_one({
            "role": "employee",
            "is_active": True,
            "department_id": department_id,
            "assigned_buildings": {"$regex": f"^{re.escape(v)}$", "$options": "i"}
        })
        if emp:
            return emp

    # 2. Substring or direct element match
    for v in variants:
        emp = users.find_one({
            "role": "employee",
            "is_active": True,
            "department_id": department_id,
            "assigned_buildings": {"$in": [v, v.title(), v.lower(), v.upper()]}
        })
        if emp:
            return emp

    return None

def create_or_cluster_issue(
    student_id: ObjectId,
    title: str,
    description: str,
    department_id: ObjectId,
    location_type: str,
    other_location_detail: str,
    building: str,
    floor: str,
    room: str,
    image_paths: list
):
    """
    Submits a new defect or clusters it with an existing open defect at the same location.
    Directly allocates hostel issues to employees on duty for that building.
    Returns: (issue_doc, is_new, message)
    """
    issues = get_issues_collection()
    normalized_key = normalize_location_key(building, floor, room)
    
    # Check if there is an active (REPORTED, ASSIGNED, or IN_PROGRESS) issue at this location
    existing_issue = issues.find_one({
        "department_id": department_id,
        "location.normalized_key": normalized_key,
        "status": {"$in": ["REPORTED", "ASSIGNED", "IN_PROGRESS"]}
    })
    
    if existing_issue:
        # Check if student is already linked to this issue
        reported_by = existing_issue.get("reported_by")
        co_affected = existing_issue.get("co_affected_students", [])
        
        if reported_by == student_id or student_id in co_affected:
            return existing_issue, False, "You have already raised/subscribed to this existing issue at this location."
        
        # Cluster this student into the existing issue
        new_count = existing_issue.get("report_count", 1) + 1
        new_priority = calculate_priority_from_count(new_count)
        
        update_data = {
            "$addToSet": {"co_affected_students": student_id},
            "$inc": {"report_count": 1},
            "$set": {
                "priority": new_priority,
                "updated_at": datetime.utcnow()
            }
        }
        
        # Add new photos to image list if provided
        if image_paths:
            update_data["$push"] = {"images": {"$each": image_paths}}
            
        issues.update_one({"_id": existing_issue["_id"]}, update_data)
        updated_doc = issues.find_one({"_id": existing_issue["_id"]})
        
        return updated_doc, False, f"Linked to existing hotspot! Urgency auto-escalated to {new_priority} ({new_count} students affected)."

    # Find technician on duty for this building and department
    on_duty_emp = find_on_duty_employee(building, department_id)
    initial_status = "ASSIGNED" if on_duty_emp else "REPORTED"
    assigned_to_info = None
    if on_duty_emp:
        assigned_to_info = {
            "employee_id": on_duty_emp["_id"],
            "name": on_duty_emp.get("name"),
            "employee_code": on_duty_emp.get("employee_id"),
            "phone": on_duty_emp.get("phone"),
            "allocated_at": datetime.utcnow()
        }

    # If no existing open issue, create a brand new issue
    ticket_id = generate_ticket_id()
    new_doc = {
        "ticket_id": ticket_id,
        "title": title.strip(),
        "description": description.strip(),
        "department_id": department_id,
        "location": {
            "location_type": location_type,
            "other_location_detail": (other_location_detail or '').strip(),
            "building_or_block": (building or '').strip(),
            "floor": (floor or '').strip(),
            "room_or_area": (room or '').strip(),
            "normalized_key": normalized_key
        },
        "images": image_paths or [],
        "reported_by": student_id,
        "co_affected_students": [],
        "report_count": 1,
        "status": initial_status,
        "assigned_to": assigned_to_info,
        "priority": "LOW",
        "resolution_notes": "",
        "resolution_image": "",
        "resolved_at": None,
        "resolved_by": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = issues.insert_one(new_doc)
    new_doc["_id"] = result.inserted_id
    
    if on_duty_emp:
        feedback_msg = f"Defect reported! Ticket #{ticket_id} has been directly allocated to on-duty technician {on_duty_emp['name']} for {building}."
    else:
        feedback_msg = f"Defect reported! Ticket #{ticket_id} has been submitted to Operations Command."
        
    return new_doc, True, feedback_msg


def resolve_issue_and_notify(
    issue_id: ObjectId,
    admin_id: ObjectId,
    resolution_notes: str,
    resolution_image: str = ""
):
    """
    Marks an issue as RESOLVED and broadcasts notifications to all affected students in real time.
    """
    issues = get_issues_collection()
    notifications = get_notifications_collection()
    
    issue = issues.find_one({"_id": issue_id})
    if not issue:
        return False, "Issue not found"
        
    resolved_time = datetime.utcnow()
    
    # Update issue status
    issues.update_one(
        {"_id": issue_id},
        {
            "$set": {
                "status": "RESOLVED",
                "resolution_notes": resolution_notes.strip(),
                "resolution_image": resolution_image,
                "resolved_at": resolved_time,
                "resolved_by": admin_id,
                "updated_at": resolved_time
            }
        }
    )
    
    # Collect all recipient student IDs (reporter + all co-affected)
    primary_reporter = issue.get("reported_by")
    co_affected = issue.get("co_affected_students", [])
    
    all_recipients = set()
    if primary_reporter:
        all_recipients.add(primary_reporter)
    for sid in co_affected:
        all_recipients.add(sid)
        
    loc = issue.get("location", {})
    loc_name = f"{loc.get('building_or_block', '')} - {loc.get('room_or_area', '')}"
    
    # Create notification docs
    notification_docs = []
    for student_id in all_recipients:
        notif = {
            "recipient_id": student_id,
            "issue_id": issue_id,
            "ticket_id": issue.get("ticket_id"),
            "title": f"Defect Resolved: {loc_name}",
            "message": f"Your reported issue ({issue.get('title')}) has been marked as RESOLVED. Note: {resolution_notes.strip()}",
            "is_read": False,
            "created_at": resolved_time
        }
        notification_docs.append(notif)
        
    if notification_docs:
        notifications.insert_many(notification_docs)
        
    # Push real-time SSE notifications to online students
    for student_id in all_recipients:
        hub.notify_user(
            str(student_id),
            {
                "type": "issue_resolved",
                "ticket_id": issue.get("ticket_id"),
                "location": loc_name,
                "title": f"Defect Resolved: {loc_name}",
                "message": f"Your reported issue has been resolved: {resolution_notes.strip()}",
                "timestamp": resolved_time.strftime("%I:%M %p")
            }
        )
        
    return True, f"Issue resolved and notifications broadcast to {len(all_recipients)} student(s)."


def save_uploaded_file(uploaded_file, subfolder="issues"):
    """Saves an uploaded image into media directory and returns web URL."""
    if not uploaded_file:
        return None
        
    upload_dir = settings.BASE_DIR / 'media' / subfolder
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if not ext:
        ext = ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = upload_dir / unique_filename
    
    with open(dest_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
            
    return f"{settings.MEDIA_URL}{subfolder}/{unique_filename}"
