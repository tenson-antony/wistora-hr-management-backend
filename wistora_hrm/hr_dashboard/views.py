
from django.utils import timezone
from django.db.models import Count

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from admin_dashboard.models import (
    Department,
    Designation,
    Employee,
    LeaveRequest,
    AttendanceRecord,
)

from admin_dashboard.serializers import (
    DepartmentSerializer,
    DesignationSerializer,
    EmployeeSerializer,
)

from admin_dashboard.permissions import IsAdminOrHRRole

from .serializers import (
    HRLeaveRequestSerializer,
    HRAttendanceRecordSerializer,
)


# --------------------------------------------------
# COMMON HR PERMISSIONS
# --------------------------------------------------

HR_PERMISSIONS = [IsAuthenticated, IsAdminOrHRRole]


# --------------------------------------------------
# 1. HR DASHBOARD OVERVIEW
# --------------------------------------------------

class HRDashboardOverviewAPIView(APIView):
    permission_classes = HR_PERMISSIONS

    def get(self, request):

        today = timezone.localdate()

        data = {
            "total_employees": Employee.objects.count(),

            "active_employees": Employee.objects.filter(
                status="active"
            ).count(),

            "inactive_employees": Employee.objects.filter(
                status="inactive"
            ).count(),

            "total_departments": Department.objects.count(),

            "total_designations": Designation.objects.count(),

            "total_leave_requests": LeaveRequest.objects.count(),

            "pending_leaves": LeaveRequest.objects.filter(
                status="pending"
            ).count(),

            "approved_leaves": LeaveRequest.objects.filter(
                status="approved"
            ).count(),

            "rejected_leaves": LeaveRequest.objects.filter(
                status="rejected"
            ).count(),

            "today_attendance": AttendanceRecord.objects.filter(
                date=today
            ).count(),

            "present_today": AttendanceRecord.objects.filter(
                date=today,
                status="present"
            ).count(),

            "absent_today": AttendanceRecord.objects.filter(
                date=today,
                status="absent"
            ).count(),

            "late_today": AttendanceRecord.objects.filter(
                date=today,
                status="late"
            ).count(),
        }

        return Response(data)


# --------------------------------------------------
# 2. EMPLOYEE MANAGEMENT
# --------------------------------------------------

class HREmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.select_related(
        "user",
        "department",
        "designation",
        "reporting_manager",
    ).all()

    serializer_class = EmployeeSerializer
    permission_classes = HR_PERMISSIONS


# --------------------------------------------------
# 3. DEPARTMENT MANAGEMENT
# --------------------------------------------------

class HRDepartmentViewSet(viewsets.ModelViewSet):

    queryset = Department.objects.select_related(
        "department_head"
    ).all()

    serializer_class = DepartmentSerializer
    permission_classes = HR_PERMISSIONS


# --------------------------------------------------
# 4. DESIGNATION MANAGEMENT
# --------------------------------------------------

class HRDesignationViewSet(viewsets.ModelViewSet):

    queryset = Designation.objects.all()

    serializer_class = DesignationSerializer
    permission_classes = HR_PERMISSIONS


# --------------------------------------------------
# 5. LEAVE MANAGEMENT
# --------------------------------------------------

class HRLeaveRequestViewSet(viewsets.ModelViewSet):

    queryset = LeaveRequest.objects.select_related(
        "employee",
        "reviewed_by",
    ).all()

    serializer_class = HRLeaveRequestSerializer
    permission_classes = HR_PERMISSIONS

    def get_reviewer(self):
        try:
            return self.request.user.employee_profile
        except Employee.DoesNotExist:
            return None

    def review_leave(self, request, decision):

        leave = self.get_object()

        if leave.status != "pending":
            return Response(
                {
                    "error": "Only pending leave requests can be reviewed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reviewer = self.get_reviewer()

        if reviewer is None:
            return Response(
                {
                    "error": "Your user account must be linked to an employee profile before reviewing leave requests."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = decision
        leave.reviewed_by = reviewer
        leave.reviewed_at = timezone.now()

        leave.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
            ]
        )

        serializer = self.get_serializer(leave)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):

        return self.review_leave(request, "approved")

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):

        return self.review_leave(request, "rejected")


# --------------------------------------------------
# 6. EMPLOYEE ATTENDANCE MANAGEMENT
# --------------------------------------------------

class HRAttendanceViewSet(viewsets.ModelViewSet):

    queryset = AttendanceRecord.objects.select_related(
        "employee",
        "employee__department",
    ).all()

    serializer_class = HRAttendanceRecordSerializer
    permission_classes = HR_PERMISSIONS


# --------------------------------------------------
# 7. HR REPORTS
# --------------------------------------------------

class HRReportsAPIView(APIView):

    permission_classes = HR_PERMISSIONS

    def get(self, request):

        # Employee count grouped by department
        department_report = (
            Department.objects.annotate(
                employee_count=Count("employee")
            ).values(
                "id",
                "name",
                "employee_count",
            )
        )

        # Employee count grouped by status
        employee_status_report = (
            Employee.objects.values("status").annotate(
                total=Count("id")
            )
        )

        # Leave count grouped by status
        leave_status_report = (
            LeaveRequest.objects.values("status").annotate(
                total=Count("id")
            )
        )

        data = {
            "department_report": list(department_report),
            "employee_status_report": list(employee_status_report),
            "leave_status_report": list(leave_status_report),
        }

        return Response(data)
