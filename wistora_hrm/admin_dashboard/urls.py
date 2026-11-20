
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardOverviewAPIView,
    DepartmentViewSet,
    DesignationViewSet,
    EmployeeViewSet,
    AcademicSessionViewSet,
    SubjectViewSet,
    SchoolClassViewSet,
    ClassSubjectAssignmentViewSet,
    StudentViewSet,
    StudentEnrollmentViewSet,
    LeaveRequestViewSet,
    AttendanceRecordViewSet,
    SystemSettingViewSet,
    AuditLogViewSet,
    NotificationViewSet,
)


router = DefaultRouter()

router.register(
    'departments',
    DepartmentViewSet,
    basename='departments'
)

router.register(
    'designations',
    DesignationViewSet,
    basename='designations'
)

router.register(
    'employees',
    EmployeeViewSet,
    basename='employees'
)

router.register(
    'academic-sessions',
    AcademicSessionViewSet,
    basename='academic-sessions'
)

router.register(
    'subjects',
    SubjectViewSet,
    basename='subjects'
)

router.register(
    'classes',
    SchoolClassViewSet,
    basename='classes'
)

router.register(
    'class-subject-assignments',
    ClassSubjectAssignmentViewSet,
    basename='class-subject-assignments'
)

router.register(
    'students',
    StudentViewSet,
    basename='students'
)

router.register(
    'student-enrollments',
    StudentEnrollmentViewSet,
    basename='student-enrollments'
)

router.register(
    'leaves',
    LeaveRequestViewSet,
    basename='leaves'
)

router.register(
    'attendance',
    AttendanceRecordViewSet,
    basename='attendance'
)

router.register(
    'settings',
    SystemSettingViewSet,
    basename='settings'
)

router.register(
    'audit-logs',
    AuditLogViewSet,
    basename='audit-logs'
)

router.register(
    'notifications',
    NotificationViewSet,
    basename='notifications'
)


urlpatterns = [
    path(
        'overview/',
        DashboardOverviewAPIView.as_view(),
        name='admin-overview'
    ),

    path('', include(router.urls)),
]
