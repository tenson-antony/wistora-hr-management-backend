
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from .models import (
    Department,
    Designation,
    Employee,
    AcademicSession,
    SchoolClass,
    Subject,
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
    SchoolClassSerializer,
    SubjectSerializer,
    ClassSubjectAssignmentSerializer,
    StudentSerializer,
    StudentEnrollmentSerializer,
    LeaveRequestSerializer,
    AttendanceRecordSerializer,
    SystemSettingSerializer,
    AuditLogSerializer,
    NotificationSerializer,
)


User = get_user_model()


# =====================================================
# 1. DASHBOARD OVERVIEW
# =====================================================

class DashboardOverviewAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        today = timezone.localdate()

        data = {

            'total_employees': Employee.objects.filter(
                status='active'
            ).count(),

            'total_students': Student.objects.filter(
                status='active'
            ).count(),

            'total_departments': Department.objects.count(),

            'total_users': User.objects.filter(
                is_active=True
            ).count(),

            'pending_leaves': LeaveRequest.objects.filter(
                status='pending'
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

        }

        return Response(data, status=status.HTTP_200_OK)


# =====================================================
# 2. DEPARTMENT MANAGEMENT
# =====================================================

class DepartmentViewSet(viewsets.ModelViewSet):

    queryset = Department.objects.select_related(
        'department_head'
    ).all()

    serializer_class = DepartmentSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 3. DESIGNATION MANAGEMENT
# =====================================================

class DesignationViewSet(viewsets.ModelViewSet):

    queryset = Designation.objects.all()

    serializer_class = DesignationSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 4. EMPLOYEE MANAGEMENT
# =====================================================

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.select_related(
        'user',
        'department',
        'designation'
    ).all()

    serializer_class = EmployeeSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 5. ACADEMIC SESSION MANAGEMENT
# =====================================================

class AcademicSessionViewSet(viewsets.ModelViewSet):

    queryset = AcademicSession.objects.all()

    serializer_class = AcademicSessionSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 6. SCHOOL CLASS MANAGEMENT
# =====================================================

class SchoolClassViewSet(viewsets.ModelViewSet):

    queryset = SchoolClass.objects.select_related(
        'academic_session'
    ).prefetch_related(
        'subjects'
    ).all()

    serializer_class = SchoolClassSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 7. SUBJECT MANAGEMENT
# =====================================================

class SubjectViewSet(viewsets.ModelViewSet):

    queryset = Subject.objects.all()

    serializer_class = SubjectSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 8. CLASS SUBJECT ASSIGNMENT
# =====================================================

class ClassSubjectAssignmentViewSet(viewsets.ModelViewSet):

    queryset = ClassSubjectAssignment.objects.select_related(
        'school_class',
        'subject',
        'teacher'
    ).all()

    serializer_class = ClassSubjectAssignmentSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 9. STUDENT MANAGEMENT
# =====================================================

class StudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.all()

    serializer_class = StudentSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 10. STUDENT ENROLLMENT MANAGEMENT
# =====================================================

class StudentEnrollmentViewSet(viewsets.ModelViewSet):

    queryset = StudentEnrollment.objects.select_related(
        'student',
        'school_class',
        'school_class__academic_session'
    ).all()

    serializer_class = StudentEnrollmentSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 11. LEAVE MANAGEMENT
# =====================================================

class LeaveRequestViewSet(viewsets.ModelViewSet):

    queryset = LeaveRequest.objects.select_related(
        'employee',
        'reviewed_by'
    ).all()

    serializer_class = LeaveRequestSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_update(self, serializer):

        new_status = serializer.validated_data.get(
            'status',
            serializer.instance.status
        )

        if new_status in ['approved', 'rejected']:

            reviewer = getattr(
            self.request.user,
            'employee_profile',
            None
            )

            serializer.save(
            reviewed_by=reviewer,
            reviewed_at=timezone.now()
            )

        else:
            serializer.save()


# =====================================================
# 12. ATTENDANCE MANAGEMENT
# =====================================================

class AttendanceRecordViewSet(viewsets.ModelViewSet):

    queryset = AttendanceRecord.objects.select_related(
        'employee'
    ).all()

    serializer_class = AttendanceRecordSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 13. SYSTEM SETTINGS
# =====================================================

class SystemSettingViewSet(viewsets.ModelViewSet):

    queryset = SystemSetting.objects.all()

    serializer_class = SystemSettingSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 14. AUDIT LOG MANAGEMENT
# =====================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AuditLog.objects.select_related(
        'user'
    ).all()

    serializer_class = AuditLogSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 15. NOTIFICATION MANAGEMENT
# =====================================================

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NotificationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

    @action(
        detail=True,
        methods=['post'],
        url_path='mark-read'
    )
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
