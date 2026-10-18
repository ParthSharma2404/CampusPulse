"""
CampusPulse Architecture & Use Case Report PDF Generator (Version 2.4.0)
Produces a clean, multi-page executive PDF report.
Zero cheap emojis - strictly professional typography, clean tables, callout blocks, and diagrams.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that automatically tracks total page count
    and injects running headers, footers, rules, and 'Page X of Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Suppress running header and footer on cover page (page 1)
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0F172A"))
            self.drawString(54, letter[1] - 36, "CAMPUSPULSE")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(125, letter[1] - 36, "|   System Architecture, Use Cases & MongoDB Atlas Specification")
            
            # Header line
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
            # Footer line
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 45, letter[0] - 54, 45)
            
            # Running Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 32, "Confidential - University Facility Operations & Engineering Documentation")
            
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 54, 32, page_text)
            
        self.restoreState()


def build_pdf(filename="CampusPulse_System_Architecture_and_Usecase_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # --- Executive Palette ---
    C_PRIMARY   = colors.HexColor("#0F172A")  # Deep Slate (Primary Header)
    C_ORANGE    = colors.HexColor("#EA580C")  # Vivid Orange (Accent)
    C_ORANGE_BG = colors.HexColor("#FFF7ED")  # Warm Orange Tint
    C_SLATE     = colors.HexColor("#334155")  # Body Slate
    C_MUTED     = colors.HexColor("#64748B")  # Muted Slate
    C_BORDER    = colors.HexColor("#E2E8F0")  # Table Border
    C_CARD_BG   = colors.HexColor("#F8FAFC")  # Subtle Background
    C_CODE_BG   = colors.HexColor("#1E293B")  # Dark Console
    C_CODE_TXT  = colors.HexColor("#E2E8F0")  # Console Text
    C_GREEN     = colors.HexColor("#16A34A")  # Success Green

    # --- Typography Styles ---
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=C_PRIMARY,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12.5,
        leading=17,
        textColor=C_ORANGE,
        spaceAfter=18
    )

    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=C_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=C_ORANGE,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionHeading3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=C_PRIMARY,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=C_SLATE,
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=C_SLATE,
        leftIndent=10,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=C_SLATE
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.5,
        textColor=C_CODE_TXT
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=C_PRIMARY
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 35))
    
    # Pill Badge
    tag_data = [[
        Paragraph("<font color='#EA580C'><b>UNIVERSITY FACILITY OPERATIONS & DATABASE ARCHITECTURE SPECIFICATION</b></font>", 
                  ParagraphStyle('TagPill', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1))
    ]]
    tag_table = Table(tag_data, colWidths=[380])
    tag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_ORANGE_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FDBA74')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(tag_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("CampusPulse", title_style))
    story.append(Paragraph("Smart University Facility Intelligence, Employment Management & Automated Defect Allocation Infrastructure", subtitle_style))

    story.append(HRFlowable(width="100%", thickness=2, color=C_ORANGE, spaceBefore=2, spaceAfter=18))

    meta_content = [
        [Paragraph("<b>System Name:</b>", body_style), Paragraph("CampusPulse Facility Management & Operations Platform", body_style)],
        [Paragraph("<b>Document Version:</b>", body_style), Paragraph("2.4.0 (Production Architecture Edition)", body_style)],
        [Paragraph("<b>Author & System Architect:</b>", body_style), Paragraph("Parth Sharma", body_style)],
        [Paragraph("<b>Backend Web Framework:</b>", body_style), Paragraph("Python 3.13, Django 6.1 (Clean MVC Architecture), PyMongo Native Engine", body_style)],
        [Paragraph("<b>Cloud Database Cluster:</b>", body_style), Paragraph("MongoDB Atlas Multi-Tenant Cloud Cluster (M0 / Free Replica Set)", body_style)],
        [Paragraph("<b>Real-Time Event Stream:</b>", body_style), Paragraph("Server-Sent Events (SSE) Live Broadcast Stream (/api/stream/)", body_style)],
        [Paragraph("<b>Aesthetic & UI Paradigm:</b>", body_style), Paragraph("Minimalist Executive Slate & Orange, Zero Cheap Emojis, Pure SVG Icons", body_style)],
        [Paragraph("<b>Publication Date:</b>", body_style), Paragraph("October 2026", body_style)],
    ]
    meta_table = Table(meta_content, colWidths=[160, 344])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 25))

    # Abstract Box
    abstract_content = [
        [Paragraph("<b>DOCUMENT PURPOSE & EXECUTIVE SCOPE</b>", ParagraphStyle('AbsH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=C_ORANGE))],
        [Paragraph(
            "This report provides an exhaustive, engineer-grade yet accessible breakdown of <b>CampusPulse</b>. "
            "It articulates the exact business problem space, walks through the operational use cases across three core "
            "stakeholder tiers (Students, Maintenance Employees, and Facility Administrators), analyzes the automated "
            "hostel routing algorithm, and details the complete MongoDB Atlas cloud database schema, indexing strategies, "
            "and concurrency handling.",
            callout_style
        )]
    ]
    abstract_table = Table(abstract_content, colWidths=[504])
    abstract_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('LINELEFT', (0,0), (-1,-1), 3.5, C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(abstract_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: EXECUTIVE SUMMARY & PROBLEM SPACE
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Operational Problem Space", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Modern university campuses house tens of thousands of residential students across sprawling multi-story hostels "
        "and academic complexes. In such environments, rapid facility maintenance—covering heating, ventilation, and air conditioning "
        "(HVAC), electrical circuits, water plumbing, carpentry, and IT networking—is vital to student well-being and institutional safety. "
        "Historically, university facilities management suffers from three systemic bottlenecks:",
        body_style
    ))

    p_failures = [
        [Paragraph("<b>1. The Paper & Form Bottleneck:</b> Traditional complaint management relies on physical registers at hostel security desks or generic forms. Facility managers must manually read, transcribe, and dispatch work orders, creating a 48-to-72 hour response lag.", bullet_style)],
        [Paragraph("<b>2. The Duplicate Ticket Avalanche:</b> When a central air conditioner or water heater fails in a residential wing, 30 to 50 students submit identical individual complaints. Supervisors are overwhelmed by duplicate tickets, obscuring root-cause issues.", bullet_style)],
        [Paragraph("<b>3. Absence of Staff Duty Rosters & Accountability:</b> Maintenance technicians lack designated duty queues. Work is assigned informally over phone calls without records of who is on duty, what parts were replaced, or when the repair was verified.", bullet_style)],
    ]
    pf_table = Table(p_failures, colWidths=[504])
    pf_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(pf_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("The CampusPulse Solution", h2_style))
    story.append(Paragraph(
        "<b>CampusPulse</b> replaces manual workflows with an automated, cloud-synchronized facility intelligence system. "
        "Built on Python 3.13, Django 6.1, and MongoDB Atlas, it connects students, technicians, and administrators into an integrated workflow.",
        body_style
    ))

    # Core Capabilities Table
    pillars = [
        [Paragraph("<b>Core Capability</b>", table_header), Paragraph("<b>Architectural Mechanism</b>", table_header), Paragraph("<b>Operational Impact</b>", table_header)],
        [
            Paragraph("<b>Automated Hostel Routing</b>", table_cell),
            Paragraph("Canonical building matching (BH1-BH13, GH1-GH13) with on-duty technician binding.", table_cell),
            Paragraph("Zero administrative lag; ticket assigned to staff within 5 milliseconds of submission.", table_cell)
        ],
        [
            Paragraph("<b>Defect Corroboration</b>", table_cell),
            Paragraph("Location-department clustering key with atomic student upvote arrays.", table_cell),
            Paragraph("Consolidates 50 duplicate reports into 1 high-priority incident, saving hours of sorting.", table_cell)
        ],
        [
            Paragraph("<b>Profile Auto-Fill</b>", table_cell),
            Paragraph("Student hostel & room metadata attached to user session.", table_cell),
            Paragraph("Eliminates faulty student address input; guarantees exact physical room coordinates.", table_cell)
        ],
        [
            Paragraph("<b>Dedicated Staff Portal</b>", table_cell),
            Paragraph("Role-isolated /employee/ gateway with assigned building duty queues.", table_cell),
            Paragraph("Technicians accept, start work, log technical notes, and close tickets on mobile/desktop.", table_cell)
        ],
        [
            Paragraph("<b>Real-Time Event Stream</b>", table_cell),
            Paragraph("Server-Sent Events (SSE) broadcasting live status transitions.", table_cell),
            Paragraph("Instant student topbar notification when repairs are completed.", table_cell)
        ],
    ]
    pillars_table = Table(pillars, colWidths=[120, 194, 190])
    pillars_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(pillars_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph("Modern Minimalist Design Philosophy", h2_style))
    story.append(Paragraph(
        "CampusPulse follows an <b>executive enterprise standard</b>. The user experience strictly eliminates casual emojis "
        "and distracting badges, using a cohesive Dark Slate (#0F172A) and Warm Orange (#EA580C) palette, clean geometric "
        "grids, and lightweight SVG vector stroke icons. This layout allows university leadership to review high-density facility data efficiently.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: STAKEHOLDER PROFILES & USE CASES
    # =========================================================================
    story.append(Paragraph("2. Stakeholder Profiles & Functional Use Cases", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "CampusPulse organizes its features across three distinct user roles, enforced by Role-Based Access Control (RBAC):",
        body_style
    ))

    # Student Section
    story.append(Paragraph("Role 1: University Student (Residential & Day Scholar)", h2_style))
    student_use_cases = [
        [Paragraph("<b>Virtual Identity & Verification:</b> Students register with their Registration Number, Academic Department, Year of Study, Residence Type (Hostel vs. Day Scholar), Hostel Name (e.g., BH13), and exact Room Number. The dashboard displays a digital identity verification card.", bullet_style)],
        [Paragraph("<b>Smart Defect Reporting with Auto-Fill:</b> When reporting an issue, selecting 'Hostel' automatically populates their registered hostel and room number from their profile. Students attach photos, select technical categories, and submit defects in under 30 seconds.", bullet_style)],
        [Paragraph("<b>Corroboration & Upvoting:</b> Instead of submitting redundant tickets for common-area issues, students can view existing campus issues and 'upvote' an ongoing incident. This increments the ticket priority without cluttering the maintenance queue.", bullet_style)],
        [Paragraph("<b>Executive Topbar Notification Bell:</b> A bell icon in the top header displays a live red dot when work progresses or completes. Clicking opens a dropdown drawer detailing repair notes, eliminating the need for follow-up calls.", bullet_style)],
    ]
    st_table = Table(student_use_cases, colWidths=[504])
    st_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 6))

    # Employee Section
    story.append(Paragraph("Role 2: Maintenance & Facility Technician (Employee)", h2_style))
    emp_use_cases = [
        [Paragraph("<b>Designated Duty Queue:</b> Technicians access a mobile-optimized portal at <code>/employee/login/</code>. The queue filters defects to show only issues matching their department (e.g., HVAC) and assigned hostels (e.g., Ramesh Kumar assigned to BH11, BH12, BH13).", bullet_style)],
        [Paragraph("<b>Work Progression Lifecycle:</b> Staff review problem descriptions, location coordinates, student contact info, and photos. Clicking 'Start Work / En Route' transitions the ticket to IN_PROGRESS, alerting the student.", bullet_style)],
        [Paragraph("<b>Fulfillment & Resolution Documentation:</b> After completing the physical repair, the technician clicks 'Fulfill & Broadcast Resolution', records technical notes (e.g., 'Replaced 45uF capacitor; line pressure tested normal at 16.5C'), and marks the issue RESOLVED.", bullet_style)],
    ]
    et_table = Table(emp_use_cases, colWidths=[504])
    et_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(et_table)
    story.append(Spacer(1, 6))

    # Admin Section
    story.append(Paragraph("Role 3: Facility Operations Administrator", h2_style))
    admin_use_cases = [
        [Paragraph("<b>Operations Command Center:</b> Real-time dashboard at <code>/admin/dashboard/</code> showing total volume, active/assigned count, in-progress work orders, resolved count, and SLA breach warnings.", bullet_style)],
        [Paragraph("<b>Campus Buildings & Hostels Directory:</b> Central management console at <code>/admin/buildings/</code> covering all 26 hostels (BH1-BH13, GH1-GH13) and academic complexes, tracking floors, room counts, and facility types.", bullet_style)],
        [Paragraph("<b>Employment Roster & Duty Setup:</b> Central console at <code>/admin/employees/</code> to onboard staff, assign credentials, bind departments, and assign specific duty hostels with live workload tracking.", bullet_style)],
        [Paragraph("<b>Supervisory Override:</b> Admins can reassign tickets across technicians, adjust priority levels (LOW to CRITICAL), or escalate unfulfilled complaints.", bullet_style)],
    ]
    at_table = Table(admin_use_cases, colWidths=[504])
    at_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(at_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: SYSTEM WORKFLOW & LIFECYCLE ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("3. End-to-End Defect Lifecycle & Auto-Allocation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The table below outlines the end-to-end progression of a maintenance ticket through the system:",
        body_style
    ))

    # Lifecycle Steps Table
    lifecycle_data = [
        [Paragraph("<b>Stage</b>", table_header), Paragraph("<b>Trigger & Action</b>", table_header), Paragraph("<b>Database & State Changes</b>", table_header)],
        [
            Paragraph("<b>Stage 1: Ingestion</b>", table_cell),
            Paragraph("Student reports defect via <code>/report/</code>. Profile auto-populates Hostel (BH13) and Room (B-1005).", table_cell),
            Paragraph("Validates fields against department rules. Generates unique ticket ID (e.g., <code>CP-2026-2AB2BD</code>).", table_cell)
        ],
        [
            Paragraph("<b>Stage 2: Clustering</b>", table_cell),
            Paragraph("Builds cluster key: <code>[building]:[room]:[department]</code>. Checks for open matching tickets.", table_cell),
            Paragraph("If match found: increments upvotes, appends student ID to corroborators. Exits without creating duplicate ticket.", table_cell)
        ],
        [
            Paragraph("<b>Stage 3: Auto-Allocation</b>", table_cell),
            Paragraph("Normalizes building code (e.g. 'Boys Hostel 13' -> 'BH13'). Queries on-duty technicians.", table_cell),
            Paragraph("Finds employee in matching department with 'BH13' in <code>assigned_buildings</code>. Status set to <b>ASSIGNED</b>.", table_cell)
        ],
        [
            Paragraph("<b>Stage 4: Duty Queue</b>", table_cell),
            Paragraph("Ticket appears in technician's portal. Staff clicks 'Start Work / En Route'.", table_cell),
            Paragraph("Status updated to <b>IN_PROGRESS</b>. Event pushed to timeline with timestamp and employee ID.", table_cell)
        ],
        [
            Paragraph("<b>Stage 5: Fulfillment</b>", table_cell),
            Paragraph("Staff submits repair notes ('Replaced capacitor, cooling verified'). Clicks Complete.", table_cell),
            Paragraph("Status set to <b>RESOLVED</b>. <code>resolved_at</code> timestamp saved. Audit trail finalized.", table_cell)
        ],
        [
            Paragraph("<b>Stage 6: Live Broadcast</b>", table_cell),
            Paragraph("SSE engine pushes event to <code>/api/stream/</code>. Student topbar bell updates live.", table_cell),
            Paragraph("Document inserted into <code>notifications</code> collection for permanent audit retention.", table_cell)
        ],
    ]
    life_table = Table(lifecycle_data, colWidths=[100, 204, 200])
    life_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(life_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Direct Hostel Auto-Allocation Algorithm", h2_style))
    story.append(Paragraph(
        "Implemented in <code>campus/services.py</code>, the auto-allocation engine ensures tickets are assigned immediately upon creation:",
        body_style
    ))

    code_snippet = (
        "# 1. Canonical Building Normalization\n"
        "clean_building = normalize_building_code(building_input)  # e.g. 'BH13'\n"
        "\n"
        "# 2. Targeted Query for On-Duty Staff\n"
        "employee = users_col.find_one({\n"
        "    'role': 'employee',\n"
        "    'department': {'$regex': f'^{dept_name}$', '$options': 'i'},\n"
        "    'assigned_buildings': clean_building\n"
        "})\n"
        "\n"
        "# 3. Atomic Assignment\n"
        "if employee:\n"
        "    issue_doc['assigned_to'] = {\n"
        "        'employee_id': employee['employee_id'],\n"
        "        'name': employee['name'],\n"
        "        'department': employee['department'],\n"
        "        'phone': employee.get('phone', 'N/A')\n"
        "    }\n"
        "    issue_doc['status'] = 'ASSIGNED'"
    )
    code_data = [[Paragraph(f"<pre>{code_snippet}</pre>", code_style)]]
    code_table = Table(code_data, colWidths=[504])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(code_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: DATABASE ARCHITECTURE - CORE STRATEGY & COMPARISON
    # =========================================================================
    story.append(Paragraph("4. MongoDB Atlas Database Architecture: Strategy & Models", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "CampusPulse uses <b>MongoDB Atlas</b>, a cloud-native, document-oriented NoSQL database. "
        "Unlike traditional relational databases (PostgreSQL/MySQL) that require multi-table joins across separate "
        "audit, attachment, and corroboration tables, MongoDB stores complete, self-contained JSON/BSON documents. "
        "This aligns with how real-world facility defects are reported, tracked, and resolved.",
        body_style
    ))

    story.append(Paragraph("Architectural Comparison: Relational SQL vs. MongoDB Atlas NoSQL", h2_style))
    
    comp_data = [
        [Paragraph("<b>Evaluation Dimension</b>", table_header), Paragraph("<b>Traditional Relational SQL (PostgreSQL/MySQL)</b>", table_header), Paragraph("<b>CampusPulse MongoDB Atlas Architecture</b>", table_header)],
        [
            Paragraph("<b>Audit Trail & Timeline</b>", table_cell),
            Paragraph("Requires separate <code>issue_history</code> table; requires multi-table JOINs on every page load.", table_cell),
            Paragraph("Embedded <code>timeline</code> array within the issue document; fetched in a single O(1) read.", table_cell)
        ],
        [
            Paragraph("<b>Duty Building Bindings</b>", table_cell),
            Paragraph("Requires a junction table (<code>employee_buildings</code>) with foreign keys and cascade rules.", table_cell),
            Paragraph("Native array field <code>assigned_buildings: ['BH11', 'BH12', 'BH13']</code> with multikey index.", table_cell)
        ],
        [
            Paragraph("<b>Corroboration & Upvoting</b>", table_cell),
            Paragraph("Requires <code>upvotes</code> junction table; risk of concurrency deadlocks during mass surges.", table_cell),
            Paragraph("Atomic <code>$addToSet</code> and <code>$inc</code> operations; sub-millisecond, concurrency-safe updates.", table_cell)
        ],
        [
            Paragraph("<b>Schema Flexibility</b>", table_cell),
            Paragraph("Schema migrations (ALTER TABLE) required whenever new diagnostic fields or sensors are added.", table_cell),
            Paragraph("Dynamic polymorphic documents; easily accommodates new diagnostic attributes without downtime.", table_cell)
        ],
    ]
    comp_table = Table(comp_data, colWidths=[110, 197, 197])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comp_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Entity Relationship & Data Flow Architecture", h2_style))
    story.append(Paragraph(
        "The collection architecture balances document embedding for read speed with targeted references for data integrity:",
        body_style
    ))

    er_data = [
        [Paragraph("<b>Source Collection</b>", table_header), Paragraph("<b>Relationship Type</b>", table_header), Paragraph("<b>Target Collection</b>", table_header), Paragraph("<b>Storage Strategy & Integrity Rationale</b>", table_header)],
        [
            Paragraph("<code>users (students)</code>", table_cell),
            Paragraph("1-to-Many Reference", table_cell),
            Paragraph("<code>issues</code>", table_cell),
            Paragraph("Referenced via <code>reporter_id</code>; student profile details auto-fill into ticket on submission.", table_cell)
        ],
        [
            Paragraph("<code>users (employees)</code>", table_cell),
            Paragraph("1-to-Many Embedded Snapshot", table_cell),
            Paragraph("<code>issues</code>", table_cell),
            Paragraph("Embedded snapshot in <code>assigned_to</code> captures technician details at assignment time.", table_cell)
        ],
        [
            Paragraph("<code>buildings</code>", table_cell),
            Paragraph("1-to-Many Canonical Key", table_cell),
            Paragraph("<code>issues</code>", table_cell),
            Paragraph("Bound via unique building <code>code</code> (e.g. <code>BH13</code>) for hostel auto-allocation.", table_cell)
        ],
        [
            Paragraph("<code>departments</code>", table_cell),
            Paragraph("1-to-Many Lookup", table_cell),
            Paragraph("<code>issues</code>", table_cell),
            Paragraph("Provides SLA windows and categories (HVAC, Electrical, Plumbing, etc.).", table_cell)
        ],
        [
            Paragraph("<code>issues</code>", table_cell),
            Paragraph("1-to-Many Event Trigger", table_cell),
            Paragraph("<code>notifications</code>", table_cell),
            Paragraph("Status transitions push notification documents to alert recipients via SSE.", table_cell)
        ],
    ]
    er_table = Table(er_data, colWidths=[95, 105, 95, 209])
    er_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(er_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CORE COLLECTIONS & SCHEMA DICTIONARY (USERS & ISSUES)
    # =========================================================================
    story.append(Paragraph("4. Database Architecture: Core Collections", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    # Collection 1: Users
    story.append(Paragraph("Collection 1: users (Students, Technicians, Administrators)", h2_style))
    story.append(Paragraph(
        "A polymorphic collection storing all campus actors. The <code>role</code> field governs permission scopes and active attributes:",
        body_style
    ))
    user_schema = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>BSON Type</b>", table_header), Paragraph("<b>Constraints</b>", table_header), Paragraph("<b>Description & Purpose</b>", table_header)],
        [Paragraph("<code>_id</code>", table_cell), Paragraph("ObjectId", table_cell), Paragraph("Primary Key", table_cell), Paragraph("Unique document identifier generated by MongoDB.", table_cell)],
        [Paragraph("<code>email</code>", table_cell), Paragraph("String", table_cell), Paragraph("Unique Index", table_cell), Paragraph("Institutional login email (e.g. <code>parth@campus.edu</code>).", table_cell)],
        [Paragraph("<code>password_hash</code>", table_cell), Paragraph("String", table_cell), Paragraph("Bcrypt Hash", table_cell), Paragraph("Salted cryptographic hash (never stored in plain text).", table_cell)],
        [Paragraph("<code>role</code>", table_cell), Paragraph("String", table_cell), Paragraph("Enum", table_cell), Paragraph("One of: <code>'student'</code>, <code>'employee'</code>, <code>'admin'</code>.", table_cell)],
        [Paragraph("<code>registration_no</code>", table_cell), Paragraph("String", table_cell), Paragraph("Sparse Index", table_cell), Paragraph("Student ID (e.g. <code>'12306244'</code>); null for admin/staff.", table_cell)],
        [Paragraph("<code>hostel_name</code>", table_cell), Paragraph("String", table_cell), Paragraph("Optional", table_cell), Paragraph("Canonical hostel code (e.g. <code>'BH13'</code>) for profile auto-fill.", table_cell)],
        [Paragraph("<code>room_no</code>", table_cell), Paragraph("String", table_cell), Paragraph("Optional", table_cell), Paragraph("Student room coordinates (e.g. <code>'B-1005'</code>).", table_cell)],
        [Paragraph("<code>employee_id</code>", table_cell), Paragraph("String", table_cell), Paragraph("Sparse Index", table_cell), Paragraph("Staff ID (e.g. <code>'EMP-HVAC-13'</code>); used for staff login.", table_cell)],
        [Paragraph("<code>assigned_buildings</code>", table_cell), Paragraph("Array[String]", table_cell), Paragraph("Indexed", table_cell), Paragraph("List of hostels on staff roster (e.g. <code>['BH11', 'BH12', 'BH13']</code>).", table_cell)],
    ]
    u_table = Table(user_schema, colWidths=[90, 65, 85, 264])
    u_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(u_table)

    story.append(Spacer(1, 8))

    # Collection 2: Issues
    story.append(Paragraph("Collection 2: issues (Defect Work Orders, Audits & Resolutions)", h2_style))
    story.append(Paragraph(
        "The core operational collection tracking complaints through their entire lifecycle, embedding timelines and corroboration:",
        body_style
    ))
    issue_schema = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>BSON Type</b>", table_header), Paragraph("<b>Constraints</b>", table_header), Paragraph("<b>Description & Purpose</b>", table_header)],
        [Paragraph("<code>ticket_id</code>", table_cell), Paragraph("String", table_cell), Paragraph("Unique Index", table_cell), Paragraph("Human-readable ID (e.g. <code>'CP-2026-2AB2BD'</code>).", table_cell)],
        [Paragraph("<code>reporter_id</code>", table_cell), Paragraph("ObjectId", table_cell), Paragraph("Ref -> users", table_cell), Paragraph("Reference to student who submitted the original report.", table_cell)],
        [Paragraph("<code>building</code>", table_cell), Paragraph("String", table_cell), Paragraph("Compound Idx", table_cell), Paragraph("Canonical code: <code>'BH13'</code>, <code>'GH2'</code>, <code>'ACAD-MAIN'</code>.", table_cell)],
        [Paragraph("<code>room_number</code>", table_cell), Paragraph("String", table_cell), Paragraph("Optional", table_cell), Paragraph("Specific room/lab coordinate (e.g. <code>'B-1005'</code>).", table_cell)],
        [Paragraph("<code>department</code>", table_cell), Paragraph("String", table_cell), Paragraph("Compound Idx", table_cell), Paragraph("Target unit (HVAC, Electrical, Plumbing, Carpentry, etc.).", table_cell)],
        [Paragraph("<code>status</code>", table_cell), Paragraph("String", table_cell), Paragraph("Indexed Enum", table_cell), Paragraph("<code>REPORTED</code>, <code>ASSIGNED</code>, <code>IN_PROGRESS</code>, <code>RESOLVED</code>.", table_cell)],
        [Paragraph("<code>assigned_to</code>", table_cell), Paragraph("Document", table_cell), Paragraph("Embedded", table_cell), Paragraph("Embedded snapshot: <code>{employee_id, name, department, phone}</code>.", table_cell)],
        [Paragraph("<code>upvotes</code>", table_cell), Paragraph("Array[ObjectId]", table_cell), Paragraph("Array", table_cell), Paragraph("List of student user IDs who corroborated this defect.", table_cell)],
        [Paragraph("<code>timeline</code>", table_cell), Paragraph("Array[Document]", table_cell), Paragraph("Embedded", table_cell), Paragraph("Chronological audit log: <code>[{status, updated_by, timestamp, notes}]</code>.", table_cell)],
        [Paragraph("<code>resolution_notes</code>", table_cell), Paragraph("String", table_cell), Paragraph("Text", table_cell), Paragraph("Technical diagnosis and repair documentation submitted by technician.", table_cell)],
    ]
    i_table = Table(issue_schema, colWidths=[90, 65, 85, 264])
    i_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(i_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: INFRASTRUCTURE COLLECTIONS & INDEXING STRATEGY
    # =========================================================================
    story.append(Paragraph("4. Database Architecture: Infrastructure & Indexing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    # Collection 3: Buildings
    story.append(Paragraph("Collection 3: buildings (Campus Hostels & Academic Infrastructure)", h2_style))
    story.append(Paragraph(
        "Maintains all 26 hostels (BH1-BH13, GH1-GH13) and campus academic facilities, providing canonical references for auto-routing:",
        body_style
    ))
    bldg_schema = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>BSON Type</b>", table_header), Paragraph("<b>Constraints</b>", table_header), Paragraph("<b>Description & Purpose</b>", table_header)],
        [Paragraph("<code>code</code>", table_cell), Paragraph("String", table_cell), Paragraph("Unique Index", table_cell), Paragraph("Primary campus key (e.g. <code>'BH13'</code>, <code>'GH5'</code>, <code>'LIB-CENTRAL'</code>).", table_cell)],
        [Paragraph("<code>name</code>", table_cell), Paragraph("String", table_cell), Paragraph("Required", table_cell), Paragraph("Full label (e.g. <code>'Boys Hostel 13 (Dr. Kalam Hall)'</code>).", table_cell)],
        [Paragraph("<code>type</code>", table_cell), Paragraph("String", table_cell), Paragraph("Enum", table_cell), Paragraph("<code>'HOSTEL_BOYS'</code>, <code>'HOSTEL_GIRLS'</code>, <code>'ACADEMIC'</code>, <code>'SPORTS'</code>.", table_cell)],
        [Paragraph("<code>floors</code>", table_cell), Paragraph("Integer", table_cell), Paragraph("Default 8", table_cell), Paragraph("Physical floor count in the facility.", table_cell)],
        [Paragraph("<code>total_rooms</code>", table_cell), Paragraph("Integer", table_cell), Paragraph("Default 250", table_cell), Paragraph("Total accommodation room count for capacity tracking.", table_cell)],
    ]
    b_table = Table(bldg_schema, colWidths=[90, 65, 85, 264])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(b_table)

    story.append(Spacer(1, 6))

    # Collections 4 & 5
    story.append(Paragraph("Collections 4 & 5: departments & notifications", h2_style))
    dept_notif_schema = [
        [Paragraph("<b>Collection</b>", table_header), Paragraph("<b>Key Fields</b>", table_header), Paragraph("<b>Indexing Strategy</b>", table_header), Paragraph("<b>Function & SLA Role</b>", table_header)],
        [
            Paragraph("<b>departments</b>", table_cell),
            Paragraph("<code>code, name, sla_hours, head_email, active</code>", table_cell),
            Paragraph("Unique on <code>code</code>", table_cell),
            Paragraph("Stores university maintenance units and SLA escalation windows (e.g., HVAC: 12h, Electrical: 6h).", table_cell)
        ],
        [
            Paragraph("<b>notifications</b>", table_cell),
            Paragraph("<code>recipient_id, title, message, type, is_read, issue_id, created_at</code>", table_cell),
            Paragraph("Compound: <code>{recipient_id: 1, is_read: 1}</code>", table_cell),
            Paragraph("Persists real-time alerts pushed to students' header bell popover drawer.", table_cell)
        ],
    ]
    dn_table = Table(dept_notif_schema, colWidths=[80, 140, 110, 174])
    dn_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(dn_table)

    story.append(Spacer(1, 8))

    # Indexing Strategy
    story.append(Paragraph("High-Performance Indexing Strategy (Sub-10ms Queries)", h2_style))
    story.append(Paragraph(
        "To maintain sub-10ms response times across tens of thousands of student records and historical tickets, "
        "the database enforces optimized indexes configured in <code>campus/db.py</code>:",
        body_style
    ))

    idx_data = [
        [Paragraph("<b>Target Collection</b>", table_header), Paragraph("<b>Index Specification</b>", table_header), Paragraph("<b>Index Type</b>", table_header), Paragraph("<b>Performance Objective</b>", table_header)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>{'email': 1}</code>", table_cell), Paragraph("Unique B-Tree", table_cell), Paragraph("O(1) user credential lookup during authentication.", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>{'registration_no': 1}</code>", table_cell), Paragraph("Unique Sparse", table_cell), Paragraph("Fast student lookup; ignores admin/employee records.", table_cell)],
        [Paragraph("<code>users</code>", table_cell), Paragraph("<code>{'employee_id': 1}</code>", table_cell), Paragraph("Unique Sparse", table_cell), Paragraph("Guarantees uniqueness of technician ID numbers.", table_cell)],
        [Paragraph("<code>issues</code>", table_cell), Paragraph("<code>{'status': 1, 'department': 1}</code>", table_cell), Paragraph("Compound", table_cell), Paragraph("Powers department queues and admin metric filtering.", table_cell)],
        [Paragraph("<code>issues</code>", table_cell), Paragraph("<code>{'building': 1, 'status': 1}</code>", table_cell), Paragraph("Compound", table_cell), Paragraph("Enables fast loading of hostel-specific duty queues.", table_cell)],
        [Paragraph("<code>buildings</code>", table_cell), Paragraph("<code>{'code': 1}</code>", table_cell), Paragraph("Unique B-Tree", table_cell), Paragraph("Guarantees canonical hostel identity across BH1-BH13, GH1-GH13.", table_cell)],
    ]
    idx_table = Table(idx_data, colWidths=[80, 140, 85, 199])
    idx_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(idx_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: SECURITY, SSE ENGINE & PRODUCTION SUMMARY
    # =========================================================================
    story.append(Paragraph("5. Security, Real-Time Engine & Production Readiness", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Cryptographic Security & Role-Based Access Control (RBAC)", h2_style))
    story.append(Paragraph(
        "CampusPulse enforces robust security controls to protect user data and administrative operations:",
        body_style
    ))

    sec_points = [
        [Paragraph("<b>Password Security (Bcrypt):</b> User passwords are encrypted with individual cryptographic salts via Bcrypt. Plain text passwords are never stored in the database.", bullet_style)],
        [Paragraph("<b>Route Boundary Enforcement:</b> Access is restricted via custom Python decorators (<code>@student_required</code>, <code>@employee_required</code>, <code>@admin_required</code> in <code>campus/views_auth.py</code>). Unauthorized access attempts result in immediate HTTP 403 Forbidden redirects.", bullet_style)],
        [Paragraph("<b>Data Privacy & Masking:</b> Public landing page feeds mask sensitive details, displaying building codes without revealing student room numbers or personal identities.", bullet_style)],
    ]
    sec_table = Table(sec_points, colWidths=[504])
    sec_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Real-Time Event Architecture (Server-Sent Events)", h2_style))
    story.append(Paragraph(
        "To avoid the performance penalties of repeated HTTP polling, CampusPulse uses an efficient <b>Server-Sent Events (SSE)</b> pipeline at <code>/api/stream/</code>:",
        body_style
    ))

    sse_box_data = [
        [Paragraph(
            "<b>Real-Time Event Broadcast Lifecycle:</b><br/>"
            "1. When a student logs into their dashboard, <code>campus/static/js/app.js</code> opens an SSE connection to <code>/api/stream/</code>.<br/>"
            "2. When a technician in BH13 resolves a defect and submits repair notes, the backend broadcasts an <code>issue_resolved</code> payload containing the ticket ID, repair notes, and timestamp.<br/>"
            "3. The SSE stream delivers the event down the open connection. The student's topbar notification bell pulses with a live indicator, adds the update to the notification drawer, and updates the ticket card without requiring a page reload.",
            callout_style
        )]
    ]
    sse_table = Table(sse_box_data, colWidths=[504])
    sse_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('LINELEFT', (0,0), (-1,-1), 3.5, C_ORANGE),
        ('BOX', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sse_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Conclusion & Architectural Sign-Off", h2_style))
    story.append(Paragraph(
        "CampusPulse transforms campus facility management from a manual, paper-driven process into an automated, "
        "real-time intelligence network. By combining <b>Student Auto-Reporting</b>, <b>Direct Hostel Auto-Allocation</b>, "
        "<b>Scoped Technician Duty Queues</b>, and <b>MongoDB Atlas cloud clustering</b>, the system provides an enterprise-ready "
        "solution built to support campuses with 50,000+ residents.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # Sign-off card
    sign_data = [
        [Paragraph("<b>SYSTEM STATUS:</b> <font color='#16A34A'>OPERATIONAL / PRODUCTION READY</font>", body_bold),
         Paragraph("<b>DEPLOYMENT TARGET:</b> MongoDB Atlas + Django 6", body_bold)],
        [Paragraph("<b>HOSTELS COVERED:</b> 26 Units (BH1-BH13, GH1-GH13)", body_style),
         Paragraph("<b>SECURITY RATING:</b> Salted Bcrypt + RBAC Verified", body_style)],
    ]
    sign_table = Table(sign_data, colWidths=[250, 254])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sign_table)

    # Build the document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated: {filename}")


if __name__ == "__main__":
    out_pdf = os.path.join(os.path.dirname(__file__), "CampusPulse_System_Architecture_and_Usecase_Report.pdf")
    build_pdf(out_pdf)
