
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    DashboardOverviewAPIView,
    DepartmentViewSet,
    DesignationViewSet,
    EmployeeViewSet,
    AcademicSessionViewSet,
    SchoolClassViewSet,
    SubjectViewSet,
    ClassSubjectAssignmentViewSet,
    StudentViewSet,
    StudentEnrollmentViewSet,
    LeaveRequestViewSet,
    AttendanceRecordViewSet,
    SystemSettingViewSet,
    AuditLogViewSet,
    NotificationViewSet,
)


# =====================================================
# API ROUTER
# =====================================================

router = DefaultRouter()


# Department
router.register(
    'departments',
    DepartmentViewSet,
    basename='departments'
)


# Designation
router.register(
    'designations',
    DesignationViewSet,
    basename='designations'
)


# Employee
router.register(
    'employees',
    EmployeeViewSet,
    basename='employees'
)


# Academic Session
router.register(
    'academic-sessions',
    AcademicSessionViewSet,
    basename='academic-sessions'
)


# School Classes
router.register(
    'classes',
    SchoolClassViewSet,
    basename='classes'
)


# Subjects
router.register(
    'subjects',
    SubjectViewSet,
    basename='subjects'
)


# Class Subject Assignments
router.register(
    'class-subject-assignments',
    ClassSubjectAssignmentViewSet,
    basename='class-subject-assignments'
)


# Students
router.register(
    'students',
    StudentViewSet,
    basename='students'
)


# Student Enrollments
router.register(
    'student-enrollments',
    StudentEnrollmentViewSet,
    basename='student-enrollments'
)


# Leave Requests
router.register(
    'leaves',
    LeaveRequestViewSet,
    basename='leaves'
)


# Attendance
router.register(
    'attendance',
    AttendanceRecordViewSet,
    basename='attendance'
)


# System Settings
router.register(
    'settings',
    SystemSettingViewSet,
    basename='settings'
)


# Audit Logs
router.register(
    'audit-logs',
    AuditLogViewSet,
    basename='audit-logs'
)


# Notifications
router.register(
    'notifications',
    NotificationViewSet,
    basename='notifications'
)


# =====================================================
# URL PATTERNS
# =====================================================

urlpatterns = [

    path(
        'overview/',
        DashboardOverviewAPIView.as_view(),
        name='dashboard-overview'
    ),

    path(
        '',
        include(router.urls)
    ),

]
