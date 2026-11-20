
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TechnicalLeadEmployeeViewSet,
    TechnicalLeadStudentAttendanceViewSet,
    TechnicalLeadStudentViewSet,
    TechnicalLeadStudentEnrollmentViewSet,
    TechnicalLeadClassViewSet,
    TechnicalLeadSubjectViewSet,
    TechnicalLeadClassSubjectAssignmentViewSet,
)


# --------------------------------------------------
# CREATE ROUTER
# --------------------------------------------------

router = DefaultRouter()


# --------------------------------------------------
# EMPLOYEE MANAGEMENT
# --------------------------------------------------

router.register(
    "employees",
    TechnicalLeadEmployeeViewSet,
    basename="technical-lead-employees"
)


# --------------------------------------------------
# STUDENT MANAGEMENT
# --------------------------------------------------

router.register(
    "students",
    TechnicalLeadStudentViewSet,
    basename="technical-lead-students"
)


# --------------------------------------------------
# STUDENT ENROLLMENT
# --------------------------------------------------

router.register(
    "student-enrollments",
    TechnicalLeadStudentEnrollmentViewSet,
    basename="technical-lead-enrollments"
)


# --------------------------------------------------
# CLASS MANAGEMENT
# --------------------------------------------------

router.register(
    "classes",
    TechnicalLeadClassViewSet,
    basename="technical-lead-classes"
)


# --------------------------------------------------
# SUBJECT MANAGEMENT
# --------------------------------------------------

router.register(
    "subjects",
    TechnicalLeadSubjectViewSet,
    basename="technical-lead-subjects"
)


# --------------------------------------------------
# TEACHER / CLASS SUBJECT ASSIGNMENTS
# --------------------------------------------------

router.register(
    "class-subject-assignments",
    TechnicalLeadClassSubjectAssignmentViewSet,
    basename="technical-lead-assignments"
)

router.register(
    r"student-attendance",
    TechnicalLeadStudentAttendanceViewSet,
    basename="technical-lead-student-attendance"
)


# --------------------------------------------------
# URL PATTERNS
# --------------------------------------------------

urlpatterns = [
    path("", include(router.urls)),
]
