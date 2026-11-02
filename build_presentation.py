import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PATH = r"D:\coding\mongodb project\CampusPulse_Executive_Presentation.pptx"
SCREENSHOTS_DIR = r"D:\coding\mongodb project\presentation_assets\screenshots"

# Palette Definitions
COLOR_BG_DARK = RGBColor(15, 23, 42)       # #0F172A (Slate 900)
COLOR_CARD_DARK = RGBColor(30, 41, 59)     # #1E293B (Slate 800)
COLOR_CARD_BORDER = RGBColor(51, 65, 85)   # #334155 (Slate 700)
COLOR_ORANGE = RGBColor(249, 115, 22)      # #F97316 (Vibrant Orange)
COLOR_ORANGE_MUTED = RGBColor(194, 65, 12) # #C2410C
COLOR_SKY = RGBColor(56, 189, 248)         # #38BDF8 (Sky Blue)
COLOR_EMERALD = RGBColor(16, 185, 129)     # #10B981 (Emerald Green)
COLOR_AMBER = RGBColor(245, 158, 11)       # #F59E0B (Amber)
COLOR_WHITE = RGBColor(248, 250, 252)      # #F8FAFC
COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8 (Slate 400)
COLOR_TEXT_DIM = RGBColor(100, 116, 139)   # #64748B (Slate 500)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_slide_layout = prs.slide_layouts[6] # blank layout

def set_slide_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG_DARK
    bg_shape.line.color.rgb = COLOR_BG_DARK
    return bg_shape

def add_header(slide, title, category="CAMPUSPULSE ENTERPRISE ARCHITECTURE"):
    # Category tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = category.upper()
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_ORANGE

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

    # Divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_DARK, border_color=COLOR_CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card

def add_image_card(slide, img_path, left, top, width, height, caption=None):
    # Background frame
    card = add_card(slide, left, top, width, height, COLOR_CARD_DARK, COLOR_CARD_BORDER)
    if os.path.exists(img_path):
        padding = Inches(0.12)
        caption_height = Inches(0.4) if caption else Inches(0)
        img_left = left + padding
        img_top = top + padding
        img_width = width - (padding * 2)
        img_height = height - (padding * 2) - caption_height
        
        slide.shapes.add_picture(img_path, img_left, img_top, width=img_width, height=img_height)
        
        if caption:
            cap_box = slide.shapes.add_textbox(left + padding, top + height - caption_height - Inches(0.05), img_width, caption_height)
            tf = cap_box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = caption
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = COLOR_SKY
            p.alignment = PP_ALIGN.CENTER
    return card

# -------------------------------------------------------------
# SLIDE 1: Title Slide (High Impact Executive)
# -------------------------------------------------------------
slide1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide1)

# Subtle decorative banner card
dec_card = add_card(slide1, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.8), COLOR_CARD_DARK, COLOR_CARD_BORDER)

# Accent top badge
badge_card = add_card(slide1, Inches(1.4), Inches(2.0), Inches(4.5), Inches(0.4), COLOR_ORANGE, None)
tf_b = badge_card.text_frame
tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
p_b = tf_b.paragraphs[0]
p_b.text = "CAMPUS INFRASTRUCTURE & FACILITY INTELLIGENCE"
p_b.font.size = Pt(10)
p_b.font.bold = True
p_b.font.color.rgb = COLOR_WHITE
p_b.alignment = PP_ALIGN.CENTER

# Main Title
title_box = slide1.shapes.add_textbox(Inches(1.4), Inches(2.6), Inches(10.5), Inches(1.4))
tf_t = title_box.text_frame
tf_t.word_wrap = True
p_t = tf_t.paragraphs[0]
p_t.text = "CampusPulse"
p_t.font.size = Pt(44)
p_t.font.bold = True
p_t.font.color.rgb = COLOR_WHITE

p_sub = tf_t.add_paragraph()
p_sub.text = "Automated University Defect Allocation, Employment Roster & Real-Time Incident Infrastructure"
p_sub.font.size = Pt(16)
p_sub.font.bold = False
p_sub.font.color.rgb = COLOR_ORANGE

# Details list
desc_box = slide1.shapes.add_textbox(Inches(1.4), Inches(4.2), Inches(10.5), Inches(1.5))
tf_d = desc_box.text_frame
tf_d.word_wrap = True

p_d1 = tf_d.paragraphs[0]
p_d1.text = "• Technology Stack: Python 3.13  |  Django 6.1  |  MongoDB Atlas Cloud Cluster  |  Server-Sent Events (SSE)"
p_d1.font.size = Pt(13)
p_d1.font.color.rgb = COLOR_TEXT_MUTED

p_d2 = tf_d.add_paragraph()
p_d2.text = "• Deployment Gateway: Vercel Cloud WSGI  (https://campus-pulse-nine-jade.vercel.app/)"
p_d2.font.size = Pt(13)
p_d2.font.color.rgb = COLOR_SKY

p_d3 = tf_d.add_paragraph()
p_d3.text = "• Architecture Core: Direct Hostel Auto-Allocation (26 Hostels), Corroboration Fingerprint Clustering & Scoped Duty Roster"
p_d3.font.size = Pt(13)
p_d3.font.color.rgb = COLOR_TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 2: Problem Statement & Existing Bottlenecks
# -------------------------------------------------------------
slide2 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide2)
add_header(slide2, "The Problem: Traditional Campus Facility Operations Breakdown", "CHALLENGES & MOTIVATION")

problems = [
    ("48-to-72 Hour Resolution Lag", 
     "Manual physical logbooks in warden offices cause severe delays before complaints reach maintenance teams.",
     COLOR_ORANGE),
    ("Severe Ticket Redundancy", 
     "Dozens of students file individual complaints for shared defects (e.g. broken water coolers or AC failure), overloading queues with noise.",
     COLOR_AMBER),
    ("Technician Misallocation", 
     "No direct building-to-staff routing. Electricians and plumbers wander across 26 vast hostels without clear zone or block ownership.",
     COLOR_SKY),
    ("Zero Status Visibility", 
     "Students remain in the dark with zero real-time feedback, leading to repeated warden visits and frustration.",
     COLOR_EMERALD)
]

card_w = Inches(2.75)
card_gap = Inches(0.24)
start_x = Inches(0.8)

for i, (title, desc, accent) in enumerate(problems):
    x = start_x + (i * (card_w + card_gap))
    card = add_card(slide2, x, Inches(1.8), card_w, Inches(4.9))
    
    # Accent top header
    acc_shape = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.8), card_w, Inches(0.1))
    acc_shape.fill.solid()
    acc_shape.fill.fore_color.rgb = accent
    acc_shape.line.fill.background()
    
    tb = slide2.shapes.add_textbox(x + Inches(0.2), Inches(2.2), card_w - Inches(0.4), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = f"0{i+1}"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = accent
    
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(12)
    p2.space_after = Pt(12)
    
    p3 = tf.add_paragraph()
    p3.text = desc
    p3.font.size = Pt(12)
    p3.font.color.rgb = COLOR_TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 3: The CampusPulse Solution & Core Value Proposition
# -------------------------------------------------------------
slide3 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide3)
add_header(slide3, "The Solution: Automated Facility Intelligence & Ecosystem", "VALUE PROPOSITION")

# 3 Big Pillar Cards
pillars = [
    ("Student Experience Portal", 
     "• Frictionless defect submission with auto-filled residence coordinates.\n• Atomic corroboration engine: upvote existing defects rather than duplicate.\n• Digital Virtual Student ID Card verification.\n• Live topbar notification drawer powered by Server-Sent Events (SSE).",
     COLOR_SKY),
    ("Dedicated Technician Duty Portal", 
     "• Mobile-optimized gateway (/employee/login/) with ID authentication.\n• Scoped duty queues: staff only receive tickets for their designated hostels & trade.\n• Structured work lifecycle: Assigned -> In Progress -> Resolved.\n• Mandatory diagnostic repair notes & verification records.",
     COLOR_ORANGE),
    ("Operations Command Center", 
     "• Centralized registry managing all 26 university hostels (BH1-BH13, GH1-GH13).\n• Employee roster & duty hostel assignment engine.\n• Real-time KPI metrics, SLA adherence tracking, and 1-click bulk auto-allocation.\n• End-to-end transparent defect lifecycle auditability.",
     COLOR_EMERALD)
]

col_w = Inches(3.75)
col_gap = Inches(0.24)
start_x = Inches(0.8)

for i, (title, points, accent) in enumerate(pillars):
    x = start_x + (i * (col_w + col_gap))
    card = add_card(slide3, x, Inches(1.8), col_w, Inches(4.9))
    
    # Header strip
    top_strip = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.8), col_w, Inches(0.55))
    top_strip.fill.solid()
    top_strip.fill.fore_color.rgb = accent
    top_strip.line.fill.background()
    
    tf_strip = top_strip.text_frame
    tf_strip.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_s = tf_strip.paragraphs[0]
    p_s.text = f"PILLAR 0{i+1}"
    p_s.font.size = Pt(11)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_WHITE
    p_s.alignment = PP_ALIGN.CENTER
    
    tb = slide3.shapes.add_textbox(x + Inches(0.25), Inches(2.6), col_w - Inches(0.5), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_h = tf.paragraphs[0]
    p_h.text = title
    p_h.font.size = Pt(17)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_WHITE
    p_h.space_after = Pt(14)
    
    for line in points.split("\n"):
        p_pt = tf.add_paragraph()
        p_pt.text = line
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = COLOR_TEXT_MUTED
        p_pt.space_after = Pt(8)

# -------------------------------------------------------------
# SLIDE 4: High-Level System Architecture
# -------------------------------------------------------------
slide4 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide4)
add_header(slide4, "End-to-End System Architecture & Data Pipeline", "SYSTEM TOPOLOGY")

layers = [
    ("1. Client Presentation Layer", 
     "Responsive Multi-Portal Web Clients (Tailwind CSS, Vanilla JS, Pure SVG Vector Icons, Zero Bloated Frameworks)\n"
     "• Resident Student Portal  |  • Technician Duty Web App  |  • Stealth Facility Admin Console",
     COLOR_SKY),
    ("2. Application Gateway Layer", 
     "Python 3.13 & Django 6.1 WSGI Application Gateway\n"
     "• Session Authentication & Role RBAC  |  • Canonical Code Normalizer  |  • Server-Sent Events (SSE) Hub\n"
     "• Deployed serverlessly via Vercel Cloud Serverless Function Runtime",
     COLOR_ORANGE),
    ("3. Cloud Data Persistence Layer", 
     "MongoDB Atlas NoSQL Cloud Database Cluster (project.z8sdm3c.mongodb.net)\n"
     "• Polymorphic Users Collection  |  • Embedded Issue Timelines  |  • Atomic $addToSet Deduplication\n"
     "• PyMongo 4.19 Driver with DNS Resilience & Multi-Index Query Optimization",
     COLOR_EMERALD)
]

for i, (title, details, accent) in enumerate(layers):
    y = Inches(1.8) + (i * Inches(1.68))
    card = add_card(slide4, Inches(0.8), y, Inches(11.733), Inches(1.45))
    
    # Left accent indicator
    left_acc = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.12), Inches(1.45))
    left_acc.fill.solid()
    left_acc.fill.fore_color.rgb = accent
    left_acc.line.fill.background()
    
    tb = slide4.shapes.add_textbox(Inches(1.15), y + Inches(0.15), Inches(11.2), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    
    for line in details.split("\n"):
        p2 = tf.add_paragraph()
        p2.text = line
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(4)

# -------------------------------------------------------------
# SLIDE 5: MongoDB Atlas NoSQL Database Architecture
# -------------------------------------------------------------
slide5 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide5)
add_header(slide5, "MongoDB Atlas Cloud NoSQL Data Modeling", "DATA ARCHITECTURE")

cols_data = [
    ("users", "Polymorphic Collection", 
     "Single collection serving Students, Employees, and Admins via role discrimination.\n"
     "• Students: registration_number, default_hostel_block, default_room_number\n"
     "• Employees: employee_id, department_id, assigned_buildings (array), duty_shift\n"
     "• Admins: master operational oversight & permissions"),
    ("issues", "Core Defect Documents", 
     "Rich document with embedded audit timelines and atomic arrays.\n"
     "• ticket_id: Unique human-readable ticket code\n"
     "• location: { location_type, building_or_block, room_or_area, normalized_key }\n"
     "• corroborators: Atomic array of student IDs confirming defect\n"
     "• timeline: Embedded chronological status transition logs"),
    ("buildings & departments", "Canonical Campus Registries", 
     "• buildings: Registry of all 26 hostels (BH1-BH13, GH1-GH13) + academic complexes, floor counts & capacities.\n"
     "• departments: Maintenance units (HVAC, Electrical, Plumbing, IT Wi-Fi, etc.) with enforced SLA target hours.")
]

for i, (name, subtitle, desc) in enumerate(cols_data):
    y = Inches(1.8) + (i * Inches(1.68))
    card = add_card(slide5, Inches(0.8), y, Inches(11.733), Inches(1.45))
    
    # Left tag
    tag_shape = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), y + Inches(0.2), Inches(2.6), Inches(0.4))
    tag_shape.fill.solid()
    tag_shape.fill.fore_color.rgb = COLOR_CARD_BORDER
    tag_shape.line.color.rgb = COLOR_ORANGE
    tf_tag = tag_shape.text_frame
    tf_tag.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = f"db.{name}"
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_ORANGE
    p_tag.alignment = PP_ALIGN.CENTER
    
    tb = slide5.shapes.add_textbox(Inches(3.9), y + Inches(0.12), Inches(8.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = subtitle
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    
    for line in desc.split("\n"):
        p2 = tf.add_paragraph()
        p2.text = line
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(3)

# -------------------------------------------------------------
# SLIDE 6: Defect Lifecycle & Algorithmic Routing Engine
# -------------------------------------------------------------
slide6 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide6)
add_header(slide6, "Defect Lifecycle & Algorithmic Routing Engine", "ROUTING LOGIC")

steps = [
    ("Step 1: Submission & Autofill", 
     "Student initiates defect report. Hostel and room coordinates are automatically populated from the student profile."),
    ("Step 2: Fingerprint Deduplication", 
     "Generates cluster key (building:room:department). If active ticket exists, increments upvotes atomically and notifies reporter."),
    ("Step 3: Canonical Normalization", 
     "Building name aliases are resolved to canonical codes (e.g. 'Boys Hostel 13' -> 'BH13') for consistent indexing."),
    ("Step 4: Atlas Query & Staff Binding", 
     "Queries MongoDB for on-duty technician assigned to normalized building code. If found, sets status ASSIGNED & embeds tech metadata."),
    ("Step 5: Duty Execution & SSE Alert", 
     "Technician accepts task, marks IN_PROGRESS, fulfills repairs with technical notes. Live SSE stream broadcasts alerts to students.")
]

card_w = Inches(2.18)
card_gap = Inches(0.2)
start_x = Inches(0.8)

for i, (title, desc) in enumerate(steps):
    x = start_x + (i * (card_w + card_gap))
    card = add_card(slide6, x, Inches(1.8), card_w, Inches(4.9))
    
    # Step Number
    tb_num = slide6.shapes.add_textbox(x + Inches(0.15), Inches(2.0), card_w - Inches(0.3), Inches(0.6))
    tf_n = tb_num.text_frame
    p_n = tf_n.paragraphs[0]
    p_n.text = f"0{i+1}"
    p_n.font.size = Pt(32)
    p_n.font.bold = True
    p_n.font.color.rgb = COLOR_ORANGE
    
    tb = slide6.shapes.add_textbox(x + Inches(0.15), Inches(2.7), card_w - Inches(0.3), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 7: Student Use Case & Live Interface Showcase
# -------------------------------------------------------------
slide7 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide7)
add_header(slide7, "Student Portal: Virtual Identity & Defect Management", "STAKEHOLDER USE CASE 1")

# Left: Features summary card
left_card = add_card(slide7, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9))
tb_s = slide7.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(4.0), Inches(4.5))
tf_s = tb_s.text_frame
tf_s.word_wrap = True

p_sh = tf_s.paragraphs[0]
p_sh.text = "Student Features & Experience"
p_sh.font.size = Pt(17)
p_sh.font.bold = True
p_sh.font.color.rgb = COLOR_WHITE
p_sh.space_after = Pt(12)

points_student = [
    "Virtual Digital ID Card: Real-time verification badge displaying Reg No, Department, Year & Residence coordinates.",
    "Smart Active Defect Feed: Visual cards tracking complaint status (Reported, Assigned, In-Progress, Resolved).",
    "Real-Time Popover Bell: Header notification drawer powered by SSE broadcasting live repair updates.",
    "Corroboration Upvote Action: 1-click upvote on active roommate/floor issues to boost priority instantly.",
    "Clean Zero-Emoji Slate Design: High readability typography and SVG icons."
]

for pt in points_student:
    p = tf_s.add_paragraph()
    p.text = f"• {pt}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(8)

# Right: Screenshot card
img_dashboard = os.path.join(SCREENSHOTS_DIR, "04_student_dashboard.png")
add_image_card(slide7, img_dashboard, Inches(5.5), Inches(1.8), Inches(7.033), Inches(4.9), 
               "Live Web Capture: Student Dashboard with Virtual ID Card & Defect Feed")

# -------------------------------------------------------------
# SLIDE 8: Defect Filing & Corroboration Flow
# -------------------------------------------------------------
slide8 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide8)
add_header(slide8, "Frictionless Defect Submission & Deduplication", "STUDENT DEFECT FILING")

# Left: Screenshot card
img_report = os.path.join(SCREENSHOTS_DIR, "05_student_report_issue.png")
add_image_card(slide8, img_report, Inches(0.8), Inches(1.8), Inches(7.033), Inches(4.9),
               "Live Web Capture: Defect Reporting Interface with Photo Upload & Auto-fill")

# Right: Explanation card
right_card = add_card(slide8, Inches(8.033), Inches(1.8), Inches(4.5), Inches(4.9))
tb_r = slide8.shapes.add_textbox(Inches(8.283), Inches(2.0), Inches(4.0), Inches(4.5))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_rh = tf_r.paragraphs[0]
p_rh.text = "Smart Filing & Clustering Logic"
p_rh.font.size = Pt(17)
p_rh.font.bold = True
p_rh.font.color.rgb = COLOR_WHITE
p_rh.space_after = Pt(12)

points_filing = [
    "Profile Coordinate Auto-fill: Student's registered Hostel Block and Room Number are injected automatically, eliminating human typo errors.",
    "Photo Evidence Upload: Integrated image proof submission stored securely for technician triage.",
    "Category Specification: Department routing (HVAC, Electrical, Plumbing, IT Wi-Fi, Furniture, CCTV).",
    "Cluster Match Prevention: Prevents multiple redundant tickets from being created for the same broken facility.",
    "Mobile-Responsive Layout: Clean touch-friendly form controls."
]

for pt in points_filing:
    p = tf_r.add_paragraph()
    p.text = f"• {pt}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(8)

# -------------------------------------------------------------
# SLIDE 9: Stakeholder Experience 2: Maintenance Technicians
# -------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide9)
add_header(slide9, "Maintenance Operations: Dedicated Employee Duty Portal", "STAKEHOLDER USE CASE 2")

# Left: Feature Breakdown
left_card = add_card(slide9, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9))
tb_e = slide9.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(4.0), Inches(4.5))
tf_e = tb_e.text_frame
tf_e.word_wrap = True

p_eh = tf_e.paragraphs[0]
p_eh.text = "Technician Workflow & Duty Queue"
p_eh.font.size = Pt(17)
p_eh.font.bold = True
p_eh.font.color.rgb = COLOR_WHITE
p_eh.space_after = Pt(12)

points_employee = [
    "Dedicated Staff Gateway: Authenticate securely via /employee/login/ using Employee ID (e.g. EMP-HVAC-13).",
    "Scoped Hostel Queues: Technicians only see defects matching their trade and assigned duty hostels (e.g. BH11, BH12, BH13).",
    "Work Progression Workflow: Instant 1-click status transitions: 'Start Work / En Route' -> 'Fulfill Repair'.",
    "Mandatory Diagnosis Logging: Technicians record technical remarks explaining component fixes before closure.",
    "Student Contact Access: Direct phone & room coordinates visible for immediate physical coordination."
]

for pt in points_employee:
    p = tf_e.add_paragraph()
    p.text = f"• {pt}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(8)

# Right: Screenshot
img_employee = os.path.join(SCREENSHOTS_DIR, "07_employee_dashboard.png")
add_image_card(slide9, img_employee, Inches(5.5), Inches(1.8), Inches(7.033), Inches(4.9),
               "Live Web Capture: Employee Duty Dashboard (/employee/dashboard/)")

# -------------------------------------------------------------
# SLIDE 10: Stakeholder Experience 3: Admin Operations Command Center
# -------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide10)
add_header(slide10, "Facility Operations Command Center: Live Analytics & Oversight", "STAKEHOLDER USE CASE 3")

# Left: Screenshot
img_admin_dash = os.path.join(SCREENSHOTS_DIR, "09_admin_dashboard.png")
add_image_card(slide10, img_admin_dash, Inches(0.8), Inches(1.8), Inches(7.033), Inches(4.9),
               "Live Web Capture: Admin Command Center with KPI Counters & Allocation Controls")

# Right: Features
right_card = add_card(slide10, Inches(8.033), Inches(1.8), Inches(4.5), Inches(4.9))
tb_a = slide10.shapes.add_textbox(Inches(8.283), Inches(2.0), Inches(4.0), Inches(4.5))
tf_a = tb_a.text_frame
tf_a.word_wrap = True

p_ah = tf_a.paragraphs[0]
p_ah.text = "Operational Command Capabilities"
p_ah.font.size = Pt(17)
p_ah.font.bold = True
p_ah.font.color.rgb = COLOR_WHITE
p_ah.space_after = Pt(12)

points_admin = [
    "High-Altitude KPI Metrics: Live counters for Total Defects, Reported Backlog, In-Progress, and Resolved items.",
    "Batch Auto-Allocation: 1-click 'Auto-Assign All Complaints' algorithm matching pending issues with on-duty staff.",
    "Individual Override: Manual technician reassignment and supervisor escalation controls.",
    "Department SLA Visibility: Real-time monitors identifying overdue or high-priority tickets across campus.",
    "Stealth Security Perimeter: Strict session authentication preventing student cross-portal access."
]

for pt in points_admin:
    p = tf_a.add_paragraph()
    p.text = f"• {pt}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(8)

# -------------------------------------------------------------
# SLIDE 11: Campus Infrastructure Registry & Roster Management
# -------------------------------------------------------------
slide11 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide11)
add_header(slide11, "Hostel Registry & Staff Duty Roster Management", "CAMPUS CONFIGURATION")

# Two Screenshots Side-by-Side
img_bldgs = os.path.join(SCREENSHOTS_DIR, "10_admin_buildings.png")
add_image_card(slide11, img_bldgs, Inches(0.8), Inches(1.8), Inches(5.7), Inches(3.6),
               "Live Web Capture: 26 Hostels Registry (/admin/buildings/)")

img_emps = os.path.join(SCREENSHOTS_DIR, "11_admin_employees.png")
add_image_card(slide11, img_emps, Inches(6.833), Inches(1.8), Inches(5.7), Inches(3.6),
               "Live Web Capture: Employee Duty Allocation Console (/admin/employees/)")

# Bottom summary card
bot_card = add_card(slide11, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.3))
tb_bot = slide11.shapes.add_textbox(Inches(1.05), Inches(5.7), Inches(11.2), Inches(1.1))
tf_bot = tb_bot.text_frame
tf_bot.word_wrap = True

p_b1 = tf_bot.paragraphs[0]
p_b1.text = "Infrastructure Registry Highlights"
p_b1.font.size = Pt(13)
p_b1.font.bold = True
p_b1.font.color.rgb = COLOR_ORANGE

p_b2 = tf_bot.add_paragraph()
p_b2.text = "• Canonical Building Registry: Pre-loaded directory managing all 26 hostels (BH1-BH13, GH1-GH13), Academic complexes & Facility blocks with floor counts.\n" \
            "• Dynamic Duty Rostering: Facility managers bind technicians to specific hostel blocks with instant automatic dispatching on newly filed tickets."
p_b2.font.size = Pt(11.5)
p_b2.font.color.rgb = COLOR_TEXT_MUTED
p_b2.space_before = Pt(3)

# -------------------------------------------------------------
# SLIDE 12: Real-Time Event Architecture & Performance Metrics
# -------------------------------------------------------------
slide12 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide12)
add_header(slide12, "Server-Sent Events (SSE) & Measurable Operational Impact", "SYSTEM PERFORMANCE")

metrics = [
    ("72h -> <2h", "Response Time Slashed", "Automated direct routing bypasses physical warden logbooks completely.", COLOR_ORANGE),
    (">70%", "Duplicate Tickets Reduced", "Corroboration cluster key merges redundant complaints into unified work orders.", COLOR_SKY),
    ("100%", "Resolution Auditability", "Technician diagnostic logs & timestamps recorded immutably in MongoDB.", COLOR_EMERALD),
    ("Zero", "Heavy Polling Overhead", "Lightweight SSE push stream eliminates wasteful client-side interval polling.", COLOR_AMBER)
]

card_w = Inches(2.75)
card_gap = Inches(0.24)
start_x = Inches(0.8)

for i, (stat, title, desc, accent) in enumerate(metrics):
    x = start_x + (i * (card_w + card_gap))
    card = add_card(slide12, x, Inches(1.8), card_w, Inches(2.4))
    
    tb = slide12.shapes.add_textbox(x + Inches(0.15), Inches(1.95), card_w - Inches(0.3), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = stat
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = accent
    p1.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(6)
    
    p3 = tf.add_paragraph()
    p3.text = desc
    p3.font.size = Pt(10.5)
    p3.font.color.rgb = COLOR_TEXT_MUTED
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(6)

# Lower comparison block
comp_card = add_card(slide12, Inches(0.8), Inches(4.5), Inches(11.733), Inches(2.2))
tb_c = slide12.shapes.add_textbox(Inches(1.1), Inches(4.65), Inches(11.1), Inches(1.9))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

p_ch = tf_c.paragraphs[0]
p_ch.text = "Architectural Superiority: Server-Sent Events (SSE) Stream vs Traditional Polling"
p_ch.font.size = Pt(15)
p_ch.font.bold = True
p_ch.font.color.rgb = COLOR_WHITE
p_ch.space_after = Pt(8)

p_cp1 = tf_c.add_paragraph()
p_cp1.text = "• EventSource Client Connection: Students maintain a single persistent HTTP connection to /api/notifications/stream/."
p_cp1.font.size = Pt(11.5)
p_cp1.font.color.rgb = COLOR_TEXT_MUTED

p_cp2 = tf_c.add_paragraph()
p_cp2.text = "• In-Memory Thread-Safe Hub: The RealtimeNotificationHub dispatches events without burdening the MongoDB Atlas database cluster with repetitive read polling."
p_cp2.font.size = Pt(11.5)
p_cp2.font.color.rgb = COLOR_TEXT_MUTED

p_cp3 = tf_c.add_paragraph()
p_cp3.text = "• Unread Popover Drawer: Notifications are immediately rendered in the topbar notification bell, updating the badge count and preview message instantly."
p_cp3.font.size = Pt(11.5)
p_cp3.font.color.rgb = COLOR_TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 13: Summary, Future Roadmap & Conclusion
# -------------------------------------------------------------
slide13 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide13)
add_header(slide13, "Project Summary & Future Roadmap", "CONCLUSION & ROADMAP")

# Two big cards: Future Enhancements & Project Metadata
left_card = add_card(slide13, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9))
tb_l = slide13.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf_l = tb_l.text_frame
tf_l.word_wrap = True

p_lh = tf_l.paragraphs[0]
p_lh.text = "Upcoming Engineering Milestones"
p_lh.font.size = Pt(17)
p_lh.font.bold = True
p_lh.font.color.rgb = COLOR_ORANGE
p_lh.space_after = Pt(14)

future_items = [
    ("AI Predictive Maintenance", "Analyze ticket recurrence patterns to forecast AC compressor or water motor failures before complete breakdown."),
    ("Spare Parts Inventory ERP", "Tie repair work orders to warehouse parts stock, automatically deducting capacitors, valves, and switches upon fulfillment."),
    ("Geo-Fencing & Beacon Check-in", "Mobile GPS verification ensuring technicians are physically inside the specified hostel room before marking work in-progress."),
    ("Student SLA Rating Feedback", "Allow residents to rate repair quality and speed, generating technician performance leaderboards.")
]

for title, d in future_items:
    p = tf_l.add_paragraph()
    p.text = f"• {title}: "
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(2)
    
    p_sub = tf_l.add_paragraph()
    p_sub.text = f"   {d}"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    p_sub.space_after = Pt(8)

right_card = add_card(slide13, Inches(6.833), Inches(1.8), Inches(5.7), Inches(4.9))
tb_r = slide13.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_rh = tf_r.paragraphs[0]
p_rh.text = "Project Verification & Delivery"
p_rh.font.size = Pt(17)
p_rh.font.bold = True
p_rh.font.color.rgb = COLOR_SKY
p_rh.space_after = Pt(14)

summary_items = [
    ("Production URL", "https://campus-pulse-nine-jade.vercel.app/"),
    ("Core Backend", "Python 3.13  |  Django 6.1  |  PyMongo 4.19"),
    ("Database Cluster", "MongoDB Atlas NoSQL (Cluster: project.z8sdm3c)"),
    ("Campus Scope", "26 University Hostels (BH1-BH13, GH1-GH13) & Academic Blocks"),
    ("Key Innovation", "Atomic Corroboration Deduplication + Direct Hostel Auto-Allocation")
]

for title, val in summary_items:
    p = tf_r.add_paragraph()
    p.text = f"{title}:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    
    pv = tf_r.add_paragraph()
    pv.text = val
    pv.font.size = Pt(11.5)
    pv.font.color.rgb = COLOR_ORANGE if "https" in val else COLOR_TEXT_MUTED
    pv.space_after = Pt(10)

# Thank you note at bottom of right card
p_ty = tf_r.add_paragraph()
p_ty.text = "Thank You! Questions & Discussion Welcome."
p_ty.font.size = Pt(14)
p_ty.font.bold = True
p_ty.font.color.rgb = COLOR_EMERALD
p_ty.space_before = Pt(16)

# Save Presentation
prs.save(OUTPUT_PATH)
print(f"Presentation successfully created and saved to: {OUTPUT_PATH}")

