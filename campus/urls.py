from django.urls import path
from django.shortcuts import redirect
from . import views_student, views_admin, views_employee

def root_redirect(request):
    if request.session.get('student_id'):
        return redirect('student_dashboard')
    elif request.session.get('employee_id'):
        return redirect('employee_dashboard')
    elif request.session.get('admin_id'):
        return redirect('admin_dashboard')
    return redirect('student_login')

urlpatterns = [
    # Landing & Public Routes
    path('', views_student.landing_page_view, name='landing'),
    path('login/', views_student.student_login_view, name='student_login'),
    path('register/', views_student.student_register_view, name='student_register'),
    path('logout/', views_student.student_logout_view, name='student_logout'),
    path('dashboard/', views_student.student_dashboard_view, name='student_dashboard'),
    path('report/', views_student.report_issue_view, name='report_issue'),
    
    # Real-Time SSE Stream & Notifications
    path('api/notifications/stream/', views_student.notification_stream_view, name='notification_stream'),
    path('api/notifications/mark-read/', views_student.mark_all_notifications_read_view, name='mark_notifications_read'),

    # Stealth Admin Routes (Separated Portal)
    path('admin/login/', views_admin.admin_login_view, name='admin_login'),
    path('admin/logout/', views_admin.admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', views_admin.admin_dashboard_view, name='admin_dashboard'),
    path('admin/issues/<str:issue_id>/resolve/', views_admin.admin_resolve_issue_view, name='admin_resolve_issue'),
    path('admin/issues/<str:issue_id>/auto-assign/', views_admin.admin_auto_assign_ticket_view, name='admin_auto_assign_ticket'),
    path('admin/issues/auto-assign-all/', views_admin.admin_auto_assign_all_view, name='admin_auto_assign_all'),
    path('admin/departments/', views_admin.admin_departments_view, name='admin_departments'),
    path('admin/buildings/', views_admin.admin_buildings_view, name='admin_buildings'),
    path('admin/employees/', views_admin.admin_employees_view, name='admin_employees'),

    # Dedicated Maintenance Employee Operations Portal
    path('employee/login/', views_employee.employee_login_view, name='employee_login'),
    path('employee/logout/', views_employee.employee_logout_view, name='employee_logout'),
    path('employee/dashboard/', views_employee.employee_dashboard_view, name='employee_dashboard'),
    path('employee/issues/<str:issue_id>/start/', views_employee.employee_start_work_view, name='employee_start_work'),
    path('employee/issues/<str:issue_id>/resolve/', views_employee.employee_resolve_issue_view, name='employee_resolve_issue'),
]

