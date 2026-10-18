import os
import django
from datetime import datetime, timedelta
from bson import ObjectId

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campuspulse.settings')
django.setup()

from campus.db import (
    get_users_collection,
    get_departments_collection,
    get_issues_collection,
    get_notifications_collection,
    hash_password,
    init_db
)
from campus.services import generate_ticket_id, normalize_location_key

def seed_demo_data():
    init_db()
    users = get_users_collection()
    departments = get_departments_collection()
    issues = get_issues_collection()
    notifications = get_notifications_collection()

    # Clear existing demo issues to avoid clutter
    issues.delete_many({})
    notifications.delete_many({})

    # Create Demo Students
    student1 = users.find_one({"registration_number": "21BCE1042"})
    if not student1:
        s1 = {
            "name": "Rohan Sharma",
            "registration_number": "21BCE1042",
            "email": "rohan.s@campus.edu",
            "phone": "+91 9876543210",
            "password_hash": hash_password("password123"),
            "role": "student",
            "default_hostel_block": "Boys Hostel 3",
            "default_room_number": "302",
            "created_at": datetime.utcnow()
        }
        res1 = users.insert_one(s1)
        student1 = users.find_one({"_id": res1.inserted_id})
        print(f"Seeded student: {student1['name']} ({student1['registration_number']})")

    student2 = users.find_one({"registration_number": "22BCS2018"})
    if not student2:
        s2 = {
            "name": "Ananya Iyer",
            "registration_number": "22BCS2018",
            "email": "ananya.i@campus.edu",
            "phone": "+91 9812345678",
            "password_hash": hash_password("password123"),
            "role": "student",
            "default_hostel_block": "Girls Hostel 1",
            "default_room_number": "204",
            "created_at": datetime.utcnow()
        }
        res2 = users.insert_one(s2)
        student2 = users.find_one({"_id": res2.inserted_id})
        print(f"Seeded student: {student2['name']} ({student2['registration_number']})")

    admin_user = users.find_one({"role": "admin"})

    # Departments lookup
    dept_hvac = departments.find_one({"code": "DEPT_HVAC"})
    dept_elec = departments.find_one({"code": "DEPT_ELEC"})
    dept_it = departments.find_one({"code": "DEPT_IT"})
    dept_plumb = departments.find_one({"code": "DEPT_PLUMB"})

    # 1. Hotspot Issue (Reported by Rohan, co-signed by Ananya)
    # AC Issue in Academic Block 2, Room 302
    issue1_key = normalize_location_key("Academic Block 2", "3rd Floor", "Room 302")
    issue1 = {
        "ticket_id": generate_ticket_id(),
        "title": "Split AC not cooling and water dripping heavily",
        "description": "The indoor blower unit in Room 302 is vibrating loudly, blowing hot air, and water is continuously dripping onto bench row 3.",
        "department_id": dept_hvac["_id"],
        "location": {
            "location_type": "Classroom",
            "other_location_detail": "",
            "building_or_block": "Academic Block 2",
            "floor": "3rd Floor",
            "room_or_area": "Room 302",
            "normalized_key": issue1_key
        },
        "images": [],
        "reported_by": student1["_id"],
        "co_affected_students": [student2["_id"]],
        "report_count": 2,
        "status": "REPORTED",
        "priority": "MEDIUM",
        "resolution_notes": "",
        "resolution_image": "",
        "resolved_at": None,
        "resolved_by": None,
        "created_at": datetime.utcnow() - timedelta(hours=3),
        "updated_at": datetime.utcnow() - timedelta(hours=1)
    }
    issues.insert_one(issue1)

    # 2. Electrical Issue in Boys Hostel 3
    issue2_key = normalize_location_key("Boys Hostel 3", "2nd Floor", "Room 214")
    issue2 = {
        "ticket_id": generate_ticket_id(),
        "title": "Ceiling fan regulator sparking and speed stuck",
        "description": "Switchboard sparks whenever we turn on the ceiling fan regulator in room 214. Burning plastic smell noticed.",
        "department_id": dept_elec["_id"],
        "location": {
            "location_type": "Hostel",
            "other_location_detail": "",
            "building_or_block": "Boys Hostel 3",
            "floor": "2nd Floor",
            "room_or_area": "Room 214",
            "normalized_key": issue2_key
        },
        "images": [],
        "reported_by": student1["_id"],
        "co_affected_students": [],
        "report_count": 1,
        "status": "REPORTED",
        "priority": "LOW",
        "resolution_notes": "",
        "resolution_image": "",
        "resolved_at": None,
        "resolved_by": None,
        "created_at": datetime.utcnow() - timedelta(hours=5),
        "updated_at": datetime.utcnow() - timedelta(hours=5)
    }
    issues.insert_one(issue2)

    # 3. Resolved Issue: Smart Classroom Projector
    issue3_key = normalize_location_key("Academic Block 1", "Ground Floor", "Lecture Hall 1")
    resolved_time = datetime.utcnow() - timedelta(hours=2)
    issue3 = {
        "ticket_id": generate_ticket_id(),
        "title": "Smart projector HDMI port broken and screen flickering",
        "description": "The podium HDMI connector is bent and does not transmit audio/video to the ceiling projector in LH-1.",
        "department_id": dept_it["_id"],
        "location": {
            "location_type": "Classroom",
            "other_location_detail": "",
            "building_or_block": "Academic Block 1",
            "floor": "Ground Floor",
            "room_or_area": "Lecture Hall 1",
            "normalized_key": issue3_key
        },
        "images": [],
        "reported_by": student1["_id"],
        "co_affected_students": [],
        "report_count": 1,
        "status": "RESOLVED",
        "priority": "LOW",
        "resolution_notes": "Technician replaced podium HDMI cable, calibrated ceiling projector, and verified audio/video sync.",
        "resolution_image": "",
        "resolved_at": resolved_time,
        "resolved_by": admin_user["_id"] if admin_user else None,
        "created_at": datetime.utcnow() - timedelta(days=1),
        "updated_at": resolved_time
    }
    res3 = issues.insert_one(issue3)

    # Add notification for student1 for the resolved issue
    notifications.insert_one({
        "recipient_id": student1["_id"],
        "issue_id": res3.inserted_id,
        "ticket_id": issue3["ticket_id"],
        "title": "Defect Resolved: Academic Block 1 - Lecture Hall 1",
        "message": f"Your reported defect '{issue3['title']}' has been resolved: Technician replaced podium HDMI cable and verified audio/video sync.",
        "is_read": False,
        "created_at": resolved_time
    })

    print("Demo data seeded with realistic multi-student hotspot reports and resolved issues.")

if __name__ == '__main__':
    seed_demo_data()
