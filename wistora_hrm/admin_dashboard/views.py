
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import (
    Department,
    Designation,
    Employee,
    AcademicSession,
    Subject,
    SchoolClass,
    ClassSubjectAssignment,
    Student,
    StudentEnrollment,
    LeaveRequest,
    AttendanceRecord,
    SystemSetting,
    AuditLog,
    Notification,
)

from .serializers import (
    DepartmentSerializer,
    DesignationSerializer,
    EmployeeSerializer,
    AcademicSessionSerializer,
    SubjectSerializer,
    SchoolClassSerializer,
    ClassSubjectAssignmentSerializer,
    StudentSerializer,
    StudentEnrollmentSerializer,
    LeaveRequestSerializer,
    AttendanceRecordSerializer,
    SystemSettingSerializer,
    AuditLogSerializer,
    NotificationSerializer,
)

from .permissions import IsAdminRole


# =====================================================
# 1. ADMIN DASHBOARD OVERVIEW
# =====================================================

class DashboardOverviewAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):

        today = timezone.localdate()

        data = {
            'total_employees': Employee.objects.count(),

            'active_employees': Employee.objects.filter(
                status='active'
            ).count(),

            'total_departments': Department.objects.count(),

            'total_students': Student.objects.count(),

            'active_students': Student.objects.filter(
                status='active'
            ).count(),

            'total_classes': SchoolClass.objects.count(),

            'total_subjects': Subject.objects.count(),

            'pending_leaves': LeaveRequest.objects.filter(
                status='pending'
            ).count(),

            'total_users': Employee.objects.exclude(
                user=None
            ).count(),

            'today_attendance': AttendanceRecord.objects.filter(
                date=today
            ).count(),

            'present_today': AttendanceRecord.objects.filter(
                date=today,
                status='present'
            ).count(),

            'absent_today': AttendanceRecord.objects.filter(
                date=today,
                status='absent'
            ).count(),

            'late_today': AttendanceRecord.objects.filter(
                date=today,
                status='late'
            ).count(),
        }

        return Response(data)


# =====================================================
# 2. DEPARTMENT VIEWSET
# =====================================================

class DepartmentViewSet(viewsets.ModelViewSet):

    queryset = Department.objects.select_related(
        'department_head'
    ).all()

    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 3. DESIGNATION VIEWSET
# =====================================================

class DesignationViewSet(viewsets.ModelViewSet):

    queryset = Designation.objects.all()

    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 4. EMPLOYEE VIEWSET
# =====================================================

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.select_related(
        'user',
        'department',
        'designation',
        'reporting_manager',
    ).all()

    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 5. ACADEMIC SESSION VIEWSET
# =====================================================

class AcademicSessionViewSet(viewsets.ModelViewSet):

    queryset = AcademicSession.objects.all()

    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 6. SUBJECT VIEWSET
# =====================================================

class SubjectViewSet(viewsets.ModelViewSet):

    queryset = Subject.objects.all()

    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 7. SCHOOL CLASS VIEWSET
# =====================================================

class SchoolClassViewSet(viewsets.ModelViewSet):

    queryset = SchoolClass.objects.select_related(
        'academic_session'
    ).prefetch_related('subjects').all()

    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 8. CLASS SUBJECT ASSIGNMENT VIEWSET
# =====================================================

class ClassSubjectAssignmentViewSet(viewsets.ModelViewSet):

    queryset = ClassSubjectAssignment.objects.select_related(
        'school_class',
        'subject',
        'teacher',
    ).all()

    serializer_class = ClassSubjectAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 9. STUDENT VIEWSET
# =====================================================

class StudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.all()

    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 10. STUDENT ENROLLMENT VIEWSET
# =====================================================

class StudentEnrollmentViewSet(viewsets.ModelViewSet):

    queryset = StudentEnrollment.objects.select_related(
        'student',
        'school_class',
        'school_class__academic_session',
    ).all()

    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 11. LEAVE REQUEST VIEWSET
# =====================================================

class LeaveRequestViewSet(viewsets.ModelViewSet):

    queryset = LeaveRequest.objects.select_related(
        'employee',
        'reviewed_by',
    ).all()

    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_reviewer(self):
        try:
            return self.request.user.employee_profile
        except Employee.DoesNotExist:
            return None

    def approve_or_reject(self, request, decision):

        leave = self.get_object()

        if leave.status != 'pending':
            return Response(
                {
                    'error': 'Only pending leave requests can be reviewed.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        reviewer = self.get_reviewer()

        if reviewer is None:
            return Response(
                {
                    'error': (
                        'Your user account must be linked to an '
                        'employee profile before reviewing leave.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.status = decision
        leave.reviewed_by = reviewer
        leave.reviewed_at = timezone.now()

        leave.save(
            update_fields=[
                'status',
                'reviewed_by',
                'reviewed_at',
            ]
        )

        return Response(
            {
                'message': f'Leave request {decision} successfully.',
                'leave_id': leave.id,
                'status': leave.status,
                'reviewed_by': reviewer.name,
                'reviewed_at': leave.reviewed_at,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):

        return self.approve_or_reject(
            request,
            'approved'
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):

        return self.approve_or_reject(
            request,
            'rejected'
        )


# =====================================================
# 12. ATTENDANCE VIEWSET
# =====================================================

class AttendanceRecordViewSet(viewsets.ModelViewSet):

    queryset = AttendanceRecord.objects.select_related(
        'employee'
    ).all()

    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 13. SYSTEM SETTINGS VIEWSET
# =====================================================

class SystemSettingViewSet(viewsets.ModelViewSet):

    queryset = SystemSetting.objects.all()

    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 14. AUDIT LOG VIEWSET
# =====================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AuditLog.objects.select_related(
        'user'
    ).all().order_by('-created_at')

    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# =====================================================
# 15. NOTIFICATION VIEWSET
# =====================================================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):

        notification = self.get_object()

        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return Response(
            {
                'message': 'Notification marked as read.'
            },
            status=status.HTTP_200_OK
        )
