
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HRDashboardOverviewAPIView,
    HREmployeeViewSet,
    HRDepartmentViewSet,
    HRDesignationViewSet,
    HRLeaveRequestViewSet,
    HRAttendanceViewSet,
    HRReportsAPIView,
)


# Create API router
router = DefaultRouter()

# Employee management
router.register(
    "employees",
    HREmployeeViewSet,
    basename="hr-employees"
)

# Department management
router.register(
    "departments",
    HRDepartmentViewSet,
    basename="hr-departments"
)

# Designation management
router.register(
    "designations",
    HRDesignationViewSet,
    basename="hr-designations"
)

# Leave management
router.register(
    "leaves",
    HRLeaveRequestViewSet,
    basename="hr-leaves"
)

# Attendance management
router.register(
    "attendance",
    HRAttendanceViewSet,
    basename="hr-attendance"
)


urlpatterns = [

    # HR dashboard overview
    path(
        "overview/",
        HRDashboardOverviewAPIView.as_view(),
        name="hr-overview"
    ),

    # HR reports
    path(
        "reports/",
        HRReportsAPIView.as_view(),
        name="hr-reports"
    ),

    # All router URLs
    path("", include(router.urls)),
]
