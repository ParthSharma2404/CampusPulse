import os
import queue
import threading
from datetime import datetime
import pymongo
from bson import ObjectId
import bcrypt
from django.conf import settings

_client = None
_db = None

def get_db():
    """Returns singleton MongoDB database instance via PyMongo with robust DNS fallback."""
    global _client, _db
    if _db is None:
        try:
            import dns.resolver
            r = dns.resolver.get_default_resolver()
            r.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
        except Exception:
            pass

        uri = getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = getattr(settings, 'MONGODB_DB_NAME', 'campuspulse_db')
        _client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=8000)
        _db = _client[db_name]
    return _db

# Collections helpers
def get_users_collection():
    return get_db()['users']

def get_departments_collection():
    return get_db()['departments']

def get_issues_collection():
    return get_db()['issues']

def get_notifications_collection():
    return get_db()['notifications']

def get_buildings_collection():
    return get_db()['buildings']


# In-Memory Real-Time SSE Hub for Instant Browser Alerts
class RealtimeNotificationHub:
    def __init__(self):
        self._lock = threading.Lock()
        # Mapping from user_id_str -> list of queue.Queue
        self._subscribers = {}

    def subscribe(self, user_id_str):
        q = queue.Queue(maxsize=50)
        with self._lock:
            if user_id_str not in self._subscribers:
                self._subscribers[user_id_str] = []
            self._subscribers[user_id_str].append(q)
        return q

    def unsubscribe(self, user_id_str, q):
        with self._lock:
            if user_id_str in self._subscribers:
                if q in self._subscribers[user_id_str]:
                    self._subscribers[user_id_str].remove(q)
                if not self._subscribers[user_id_str]:
                    del self._subscribers[user_id_str]

    def notify_user(self, user_id_str, event_data):
        with self._lock:
            queues = list(self._subscribers.get(str(user_id_str), []))
        for q in queues:
            try:
                q.put_nowait(event_data)
            except queue.Full:
                pass

hub = RealtimeNotificationHub()


def hash_password(plain_password: str) -> str:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def init_db():
    """Initializes collections, indexes, and default campus departments & admin."""
    db = get_db()
    users = db['users']
    departments = db['departments']
    issues = db['issues']
    notifications = db['notifications']

    # Indexes
    try:
        users.create_index("email", unique=True)
        users.create_index("registration_number", unique=True, sparse=True)
        departments.create_index("code", unique=True)
        issues.create_index("ticket_id", unique=True)
        issues.create_index("location.normalized_key")
        issues.create_index("status")
        issues.create_index("department_id")
        issues.create_index("reported_by")
        notifications.create_index([("recipient_id", 1), ("is_read", 1), ("created_at", -1)])
        db['buildings'].create_index("code", unique=True)
    except Exception as e:
        print(f"Index creation note: {e}")

    # Seed Default Departments if empty
    if departments.count_documents({}) == 0:
        default_depts = [
            {
                "name": "HVAC / Air Conditioning",
                "code": "DEPT_HVAC",
                "description": "AC units, central cooling, ducts, and ventilation maintenance",
                "contact_person": "Mr. Sharma",
                "contact_email": "hvac@campus.edu",
                "contact_phone": "+91 9811223344",
                "color_tag": "#3B82F6",
                "sla_resolution_hours": 24,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Electrical & Lighting",
                "code": "DEPT_ELEC",
                "description": "Switches, wiring, power sockets, tube lights, fans, and circuit boards",
                "contact_person": "Mr. Verma",
                "contact_email": "electrical@campus.edu",
                "contact_phone": "+91 9822334455",
                "color_tag": "#F59E0B",
                "sla_resolution_hours": 12,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Plumbing & Water Works",
                "code": "DEPT_PLUMB",
                "description": "Water taps, flush tanks, drainage leaks, and drinking water filters",
                "contact_person": "Mr. Rajesh",
                "contact_email": "plumbing@campus.edu",
                "contact_phone": "+91 9833445566",
                "color_tag": "#06B6D4",
                "sla_resolution_hours": 12,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Hostel Warden & Facilities",
                "code": "DEPT_HOSTEL",
                "description": "Hostel room fixtures, door locks, balcony issues, and mess complaints",
                "contact_person": "Dr. K. Rao (Chief Warden)",
                "contact_email": "hostels@campus.edu",
                "contact_phone": "+91 9844556677",
                "color_tag": "#8B5CF6",
                "sla_resolution_hours": 24,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "IT & Campus Wi-Fi",
                "code": "DEPT_IT",
                "description": "Wi-Fi routers, LAN ports, smart board projectors, and computer lab systems",
                "contact_person": "Tech Support Center",
                "contact_email": "ithelpdesk@campus.edu",
                "contact_phone": "+91 9855667788",
                "color_tag": "#10B981",
                "sla_resolution_hours": 8,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Sanitation & Housekeeping",
                "code": "DEPT_CLEAN",
                "description": "Washroom cleanliness, garbage clearance, and campus hygiene",
                "contact_person": "Housekeeping Supervisor",
                "contact_email": "clean@campus.edu",
                "contact_phone": "+91 9866778899",
                "color_tag": "#EC4899",
                "sla_resolution_hours": 6,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Carpentry & Furniture",
                "code": "DEPT_CARP",
                "description": "Desks, chairs, podiums, broken windows, and hostel cupboards",
                "contact_person": "Workshop In-charge",
                "contact_email": "carpentry@campus.edu",
                "contact_phone": "+91 9877889900",
                "color_tag": "#D97706",
                "sla_resolution_hours": 48,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "CCTV & Surveillance",
                "code": "DEPT_CCTV",
                "description": "Security camera monitoring, control room, and emergency panic alarms",
                "contact_person": "Col. Vikram Singh",
                "contact_email": "security@campus.edu",
                "contact_phone": "+91 9888990011",
                "color_tag": "#4B5563",
                "sla_resolution_hours": 24,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        departments.insert_many(default_depts)
        print("8 default campus departments seeded successfully.")

    # Seed Default Administrator if not exists
    admin_user = users.find_one({"role": "admin"})
    if not admin_user:
        super_admin = {
            "name": "Campus Facility Administrator",
            "registration_number": "ADMIN-001",
            "email": "admin@campus.edu",
            "phone": "+91 9999999999",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "default_hostel_block": "Admin Headquarters",
            "default_room_number": "101",
            "created_at": datetime.utcnow()
        }
        users.insert_one(super_admin)
        print("Default admin created: admin@campus.edu / admin123")

    # Seed Demo Students if not exists
    student_1 = users.find_one({"registration_number": "21BCE1042"})
    if not student_1:
        student_doc = {
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
        student_1_id = users.insert_one(student_doc).inserted_id
        print("Demo student 1 created: 21BCE1042 / password123")
    else:
        student_1_id = student_1["_id"]

    student_2 = users.find_one({"registration_number": "22BCS2018"})
    if not student_2:
        student_2_doc = {
            "name": "Ananya Patel",
            "registration_number": "22BCS2018",
            "email": "ananya.p@campus.edu",
            "phone": "+91 9876543211",
            "password_hash": hash_password("password123"),
            "role": "student",
            "default_hostel_block": "Girls Hostel 2",
            "default_room_number": "415",
            "created_at": datetime.utcnow()
        }
        users.insert_one(student_2_doc)
        print("Demo student 2 created: 22BCS2018 / password123")

    # Seed Initial Defect Tickets if empty
    if issues.count_documents({}) == 0:
        hvac_dept = departments.find_one({"code": "DEPT_HVAC"})
        elec_dept = departments.find_one({"code": "DEPT_ELEC"})

        sample_issues = [
            {
                "ticket_id": "CP-2026-B18A9F",
                "title": "Split AC not cooling and water dripping heavily",
                "description": "The split AC in Room 302 has stopped blowing cool air and water is leaking steadily over study desks.",
                "department_id": str(hvac_dept["_id"]) if hvac_dept else "DEPT_HVAC",
                "location": {
                    "location_type": "Classroom",
                    "building_or_block": "Academic Block 2",
                    "room_or_area": "Room 302",
                    "normalized_key": "classroom:academic block 2:room 302"
                },
                "status": "RESOLVED",
                "priority": "HIGH",
                "reported_by": str(student_1_id),
                "co_reporters": [str(student_1_id)],
                "report_count": 2,
                "resolution_notes": "Technician replaced the blower capacitor and flushed the water drain line. AC cooling verified at 18C.",
                "resolved_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "ticket_id": "CP-2026-8B5AE2",
                "title": "Smart projector HDMI port broken and screen flickering",
                "description": "Podium HDMI transmitter is loose and classroom ceiling projector loses signal intermittently during lectures.",
                "department_id": str(elec_dept["_id"]) if elec_dept else "DEPT_ELEC",
                "location": {
                    "location_type": "Lecture Hall",
                    "building_or_block": "Academic Block 1",
                    "room_or_area": "Lecture Hall 1",
                    "normalized_key": "lecture hall:academic block 1:lecture hall 1"
                },
                "status": "RESOLVED",
                "priority": "MEDIUM",
                "reported_by": str(student_1_id),
                "co_reporters": [str(student_1_id)],
                "report_count": 1,
                "resolution_notes": "Technician replaced podium HDMI cable, calibrated ceiling projector, and verified audio/video sync.",
                "resolved_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "ticket_id": "CP-2026-3C84AA",
                "title": "Ceiling fan regulator sparking and speed stuck",
                "description": "Switchboard sparks whenever we turn on the ceiling fan regulator in room 214. Burning plastic smell noticed.",
                "department_id": str(elec_dept["_id"]) if elec_dept else "DEPT_ELEC",
                "location": {
                    "location_type": "Hostel",
                    "building_or_block": "Boys Hostel 3",
                    "room_or_area": "Room 214",
                    "normalized_key": "hostel:boys hostel 3:room 214"
                },
                "status": "REPORTED",
                "priority": "LOW",
                "reported_by": str(student_1_id),
                "co_reporters": [str(student_1_id)],
                "report_count": 1,
                "resolution_notes": "",
                "resolved_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        issues.insert_many(sample_issues)
        print("Sample defect tickets seeded successfully.")

    # Seed Campus Hostels & Buildings (BH1..BH13, GH1..GH13, Academic)
    buildings = db['buildings']
    if buildings.count_documents({}) == 0:
        default_buildings = []
        # Boys Hostels 1 to 13
        for i in range(1, 14):
            default_buildings.append({
                "code": f"BH{i}",
                "name": f"Boys Hostel {i}",
                "type": "HOSTEL_BOYS",
                "total_floors": 12 if i >= 10 else 6,
                "warden_contact": f"+91 98110{i:02d}001",
                "is_active": True,
                "created_at": datetime.utcnow()
            })
        # Girls Hostels 1 to 13
        for i in range(1, 14):
            default_buildings.append({
                "code": f"GH{i}",
                "name": f"Girls Hostel {i}",
                "type": "HOSTEL_GIRLS",
                "total_floors": 10 if i >= 8 else 5,
                "warden_contact": f"+91 98220{i:02d}002",
                "is_active": True,
                "created_at": datetime.utcnow()
            })
        # Academic & Core Facilities
        core_facilities = [
            {"code": "ACAD1", "name": "Academic Block 1", "type": "ACADEMIC", "total_floors": 5},
            {"code": "ACAD2", "name": "Academic Block 2", "type": "ACADEMIC", "total_floors": 6},
            {"code": "LIB1", "name": "Central Library", "type": "FACILITY", "total_floors": 4},
            {"code": "CAFE1", "name": "Food Court & Student Center", "type": "FACILITY", "total_floors": 2},
            {"code": "SPORT1", "name": "Indoor Sports Complex", "type": "FACILITY", "total_floors": 3},
        ]
        for f in core_facilities:
            f["warden_contact"] = "+91 9800112233"
            f["is_active"] = True
            f["created_at"] = datetime.utcnow()
            default_buildings.append(f)

        buildings.insert_many(default_buildings)
        print("Pre-seeded BH1-BH13, GH1-GH13, and campus facilities successfully.")

    # Seed Default Operational Maintenance Employees / Technicians
    hvac_dept = departments.find_one({"code": "DEPT_HVAC"})
    elec_dept = departments.find_one({"code": "DEPT_ELEC"})
    if users.count_documents({"role": "employee"}) == 0:
        sample_employees = [
            {
                "name": "Ramesh Kumar",
                "employee_id": "EMP-HVAC-13",
                "email": "ramesh.hvac@campus.edu",
                "phone": "+91 9876543210",
                "password_hash": hash_password("staff123"),
                "role": "employee",
                "department_id": hvac_dept["_id"] if hvac_dept else None,
                "assigned_buildings": ["BH13", "BH12", "BH11"],
                "duty_shift": "General Shift (8 AM - 6 PM)",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Suresh Verma",
                "employee_id": "EMP-ELEC-03",
                "email": "suresh.elec@campus.edu",
                "phone": "+91 9876543211",
                "password_hash": hash_password("staff123"),
                "role": "employee",
                "department_id": elec_dept["_id"] if elec_dept else None,
                "assigned_buildings": ["Boys Hostel 3", "BH3", "BH2", "BH1"],
                "duty_shift": "Morning Shift (7 AM - 3 PM)",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        users.insert_many(sample_employees)
        print("Sample operational maintenance employees seeded.")
