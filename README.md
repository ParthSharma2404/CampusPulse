# CampusPulse

> **Smart University Facility Intelligence, Employment Roster & Automated Defect Allocation Infrastructure**

CampusPulse is an enterprise-grade campus operations and facilities management platform built on **Python 3.13**, **Django 6.1**, and **MongoDB Atlas**. Designed to eliminate the 48-to-72 hour response lag inherent in paper logbooks and manual dispatching, CampusPulse unifies the residential student body, campus maintenance technicians, and facility administrators into an automated, real-time ecosystem.

---

## Architectural Highlights

* **Direct Hostel Auto-Allocation Engine:** Canonical building normalization (`BH1` through `BH13`, `GH1` through `GH13`) with instant on-duty technician binding and automatic ticket status escalation.
* **Corroboration & Deduplication:** Clustered fingerprints (`building:room:department`) allow students to upvote an existing defect, collapsing dozens of redundant tickets into a single high-priority incident.
* **Profile Auto-Fill:** Student residence metadata (Hostel & Room coordinates) automatically populates during defect reporting, eliminating address errors.
* **Dedicated Employee Duty Portal:** Mobile-friendly gateway (`/employee/login/`) with scoped hostel queues, work progression tracking (`ASSIGNED` -> `IN_PROGRESS` -> `RESOLVED`), and technical repair notes documentation.
* **Executive Notification Bell:** Header popover drawer with live unread indicators, eliminating the need for intrusive page-wide alert banners.
* **Real-Time Event Stream:** Lightweight Server-Sent Events (SSE) broadcasting live status transitions to student dashboards without heavy polling.
* **Executive Dark/Slate & Orange Aesthetic:** Minimalist design system, clean geometric alignment, and pure SVG stroke icons (strictly zero cheap emojis).

---

## Stakeholder Roles & Workflows

### 1. University Students (Residents & Day Scholars)
* **Virtual Identity Card:** Digital student verification card displaying Registration Number, Department, Year, and Residence coordinates.
* **Defect Reporting:** Select category (HVAC, Electrical, Plumbing, Carpentry, IT Networking, Civil), attach photo evidence, and submit. Hostel and room coordinates auto-populate from profile.
* **Corroboration:** Upvote existing incidents to increase ticket priority without creating duplicate work orders.
* **Live Notifications:** Receive real-time push alerts via the topbar notification bell when technicians start work or fulfill repairs.

### 2. Maintenance & Facility Technicians (Employees)
* **Designated Duty Queue:** Access `/employee/login/` with Employee ID or email. Queue displays only tickets matching the technician's department and assigned roster hostels (e.g., `BH11`, `BH12`, `BH13`).
* **Work Progression:** Review student contact information, defect descriptions, and photos. Transition orders to `IN_PROGRESS` via **Start Work / En Route**.
* **Fulfillment & Resolution:** Submit technical diagnosis notes (e.g., *"Replaced 45uF capacitor; line pressure tested normal at 16.5C"*) and broadcast instant resolution.

### 3. Facility Operations Administrators
* **Command Center:** Live KPI metrics (Total Volume, Active, In-Progress, Resolved, SLA breach risks).
* **Campus Buildings Console (`/admin/buildings/`):** Central directory managing all 26 hostels (`BH1-BH13`, `GH1-GH13`) and academic complexes, room capacities, and floor counts.
* **Employment Management Console (`/admin/employees/`):** Onboard technical staff, configure login credentials, bind departments, and assign specific duty hostels with live workload tracking.

---

## Defect Lifecycle & Algorithmic Routing

```
[Student Reports Defect]
         |
         v
[Auto-Fill Profile Coordinates (Hostel & Room)]
         |
         v
[Cluster Key Check: building:room:dept]
         |
         +--> [Match Found] ----> [Increment Upvotes & Add Student ID] -> (Exit)
         |
         +--> [New Defect]
                  |
                  v
         [Normalize Building Code (e.g., 'Boys Hostel 13' -> 'BH13')]
                  |
                  v
         [Query MongoDB Atlas: department + assigned_buildings: 'BH13']
                  |
                  +--> [Technician Found] ----> [Status: ASSIGNED + Embed Tech Metadata]
                  |
                  +--> [No Staff On Duty] ----> [Status: REPORTED]
                           |
                           v
                  [Technician Duty Queue (/employee/dashboard/)]
                           |
                           v
                  [Action: Start Work / En Route -> Status: IN_PROGRESS]
                           |
                           v
                  [Action: Fulfill & Record Notes -> Status: RESOLVED]
                           |
                           v
                  [SSE Broadcast to /api/stream/ -> Live Student Bell Alert]
```

---

## MongoDB Atlas Database Architecture

CampusPulse utilizes **MongoDB Atlas** NoSQL cloud clustering. Document-oriented storage enables rich embedded timelines and atomic corroboration arrays without multi-table relational joins.

### Collections Overview

| Collection | Role / Description | Primary / Unique Indexes |
| :--- | :--- | :--- |
| **`users`** | Polymorphic collection for Students, Employees, and Admins. | `email` (Unique), `registration_no` (Sparse), `employee_id` (Sparse) |
| **`issues`** | Core work orders with embedded timelines and corroboration arrays. | `ticket_id` (Unique), `status + department`, `building + status` |
| **`buildings`** | Canonical registry of all 26 hostels (`BH1-BH13`, `GH1-GH13`) & facilities. | `code` (Unique) |
| **`departments`** | Maintenance divisions (HVAC, Electrical, Plumbing, etc.) & SLA rules. | `code` (Unique) |
| **`notifications`** | Persistent alerts rendered in student header popover drawers. | `recipient_id + is_read + created_at` |

### Key Document Schemas

#### `issues` Document (Sample Structure)
```json
{
  "_id": "ObjectId('6712ab...')",
  "ticket_id": "CP-2026-2AB2BD",
  "reporter_id": "ObjectId('671290...')",
  "reporter_name": "Parth Sharma",
  "reporter_reg_no": "12306244",
  "location_type": "HOSTEL",
  "building": "BH13",
  "room_number": "B-1005",
  "department": "HVAC",
  "category": "Air Conditioning Failure",
  "title": "AC compressor tripped and blowing ambient air",
  "priority": "HIGH",
  "status": "RESOLVED",
  "assigned_to": {
    "employee_id": "EMP-HVAC-13",
    "name": "Ramesh Kumar",
    "department": "HVAC & Climate Control",
    "phone": "+91 98765 43210"
  },
  "upvotes": ["ObjectId('671291...')"],
  "upvote_count": 1,
  "timeline": [
    {
      "status": "ASSIGNED",
      "updated_by": "SYSTEM_ROUTER",
      "timestamp": "2026-10-18T17:42:00Z",
      "notes": "Direct hostel auto-allocation to Ramesh Kumar (BH13 HVAC roster)."
    },
    {
      "status": "IN_PROGRESS",
      "updated_by": "EMP-HVAC-13",
      "timestamp": "2026-10-18T17:45:00Z",
      "notes": "Technician dispatched and en route to BH13 B-1005."
    },
    {
      "status": "RESOLVED",
      "updated_by": "EMP-HVAC-13",
      "timestamp": "2026-10-18T17:58:00Z",
      "notes": "Replaced faulty dual-run capacitor. Tested compressor cycle; vent temp stabilized at 16.5C."
    }
  ],
  "resolution_notes": "Replaced faulty dual-run capacitor. Tested compressor cycle; vent temp stabilized at 16.5C.",
  "resolved_at": "2026-10-18T17:58:00Z",
  "created_at": "2026-10-18T17:42:00Z"
}
```

---

## Technical Stack

* **Language:** Python 3.13
* **Web Framework:** Django 6.1 (Clean MVC, custom authentication decorators, no legacy Django ORM overhead for core logic)
* **Database Driver:** PyMongo 4.9+ Native Client
* **Cloud Database:** MongoDB Atlas (Multi-Tenant Cloud Replica Set)
* **Real-Time Streaming:** Server-Sent Events (SSE) via streaming HTTP response
* **PDF Engine:** ReportLab 5.0 (Two-Pass Numbered Vector Generation)
* **Frontend:** Clean Vanilla CSS Design System, Responsive Layouts, SVG Icons

---

## Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ParthSharma2404/CampusPulse.git
cd CampusPulse
```

### 2. Configure Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template and fill in your MongoDB Atlas credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@project.z8sdm3c.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=campuspulse_db
SECRET_KEY=your-production-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
```

### 5. Initialize Database & Seed Default Infrastructure
Run the database initializer to create collections, indexes, departments, and all 26 campus hostels:
```bash
python manage.py runserver
```
*(On first startup, `campus/db.py` automatically initializes collections, unique indexes, 31 campus buildings, and initial staff).*

### 6. Access the Application
* **Landing Page & Portal Gateway:** `http://127.0.0.1:8000/`
* **Student Registration / Login:** `http://127.0.0.1:8000/login/`
* **Defect Reporting:** `http://127.0.0.1:8000/report/`
* **Employee Duty Portal:** `http://127.0.0.1:8000/employee/login/`
* **Facility Admin Console:** `http://127.0.0.1:8000/admin/login/`
* **Buildings Directory:** `http://127.0.0.1:8000/admin/buildings/`
* **Employment Roster:** `http://127.0.0.1:8000/admin/employees/`

---

## Pre-Seeded Demonstration Accounts

| Role | Username / Identifier | Password | Duty Assignment / Context |
| :--- | :--- | :--- | :--- |
| **Facility Admin** | `admin@campus.edu` | `admin123` | Full Campus Facility Operations Access |
| **HVAC Technician** | `EMP-HVAC-13` | `staff123` | Assigned to `BH13`, `BH12`, `BH11` |
| **Electrical Technician** | `EMP-ELEC-03` | `staff123` | Assigned to `BH3`, `BH2`, `BH1` |
| **Residential Student** | `12306244` | `student123` | Resident of `BH13`, Room `B-1005` |

---

## Architectural Documentation

A complete 8-page specification report is compiled in the repository:
* [`CampusPulse_System_Architecture_and_Usecase_Report.pdf`](CampusPulse_System_Architecture_and_Usecase_Report.pdf)

To regenerate the PDF documentation with updated system parameters:
```bash
python generate_pdf_report.py
```

---

## License

This project is developed for academic, institutional facility management, and research purposes.
Distributed under the **MIT License**.
