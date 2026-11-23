from rest_framework import viewsets

from django.db.models import Count
from django.utils import timezone
from rest_framework.views import APIView, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_dashboard.models import (
    Employee,
    Student,
    StudentAttendance,
    StudentEnrollment,
    SchoolClass,
    Subject,
    ClassSubjectAssignment,
)

from .serializers import (
    TechnicalLeadEmployeeSerializer,
    TechnicalLeadStudentSerializer,
    TechnicalLeadStudentEnrollmentSerializer,
    TechnicalLeadClassSerializer,
    TechnicalLeadSubjectSerializer,
    TechnicalLeadClassSubjectAssignmentSerializer,
    TechnicalLeadStudentAttendanceSerializer,
)

from .permissions import IsTechnicalLeadRole


# --------------------------------------------------
# COMMON TECHNICAL LEAD PERMISSIONS
# --------------------------------------------------

TECHNICAL_LEAD_PERMISSIONS = [
    IsAuthenticated,
    IsTechnicalLeadRole,
]


# --------------------------------------------------
# HELPER: GET LOGGED-IN TECHNICAL LEAD'S PROFILE
# --------------------------------------------------

def get_technical_lead_profile(user):

    try:
        return user.employee_profile
    except Employee.DoesNotExist:
        return None


# --------------------------------------------------
# 1. EMPLOYEE MANAGEMENT
# --------------------------------------------------

class TechnicalLeadEmployeeViewSet(
    viewsets.ReadOnlyModelViewSet
):
    """
    Technical Leads can only view employees
    who report directly to them.

    They cannot create, update, or delete employees.
    """

    serializer_class = TechnicalLeadEmployeeSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS

    # def get_queryset(self):

    #     user = self.request.user

    #     # Superusers can view all employees.
    #     if user.is_superuser:
    #         return Employee.objects.select_related(
    #             "department",
    #             "designation",
    #             "reporting_manager",
    #         ).all()

    #     technical_lead = get_technical_lead_profile(user)

    #     if technical_lead is None:
    #         return Employee.objects.none()

    #     return Employee.objects.select_related(
    #         "department",
    #         "designation",
    #         "reporting_manager",
    #     ).filter(
    #         reporting_manager=technical_lead
    #     )
    def get_queryset(self):

        return get_technical_lead_team(
            self.request.user
        ).select_related(
            "department",
            "designation",
            "reporting_manager",
            "user"
        )


# --------------------------------------------------
# 2. STUDENT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadStudentViewSet(viewsets.ModelViewSet):

    # queryset = Student.objects.all()
    def get_queryset(self):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        accessible_student_ids = StudentEnrollment.objects.filter(
            school_class_id__in=class_ids
        ).values_list(
            "student_id",
            flat=True
        ).distinct()

        return Student.objects.filter(
            id__in=accessible_student_ids
        ).distinct()

    serializer_class = TechnicalLeadStudentSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 3. STUDENT ENROLLMENT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadStudentEnrollmentViewSet(
    viewsets.ModelViewSet
):

    # queryset = StudentEnrollment.objects.select_related(
    #     "student",
    #     "school_class",
    #     "school_class__academic_session",
    # ).all()
    def get_queryset(self):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        return StudentEnrollment.objects.filter(
            school_class_id__in=class_ids
        ).select_related(
            "student",
            "school_class"
        )
    def perform_create(self, serializer):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        school_class = serializer.validated_data[
            "school_class"
        ]

        if not SchoolClass.objects.filter(
            id__in=class_ids,
            id=school_class.id
        ).exists():

            raise PermissionDenied(
                "You cannot create enrollments for this class."
            )

        serializer.save()

    serializer_class = TechnicalLeadStudentEnrollmentSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 4. CLASS MANAGEMENT
# --------------------------------------------------

class TechnicalLeadClassViewSet(viewsets.ModelViewSet):

    # queryset = SchoolClass.objects.select_related(
    #     "academic_session"
    # ).prefetch_related(
    #     "subjects"
    # ).all()
    def get_queryset(self):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        return SchoolClass.objects.filter(
            id__in=class_ids
        ).select_related(
            "academic_session"
        ).distinct()

    serializer_class = TechnicalLeadClassSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 5. SUBJECT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadSubjectViewSet(viewsets.ModelViewSet):

    # queryset = Subject.objects.all()
    def get_queryset(self):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        accessible_subject_ids = ClassSubjectAssignment.objects.filter(
            school_class_id__in=class_ids
        ).values_list(
            "subject_id",
            flat=True
        ).distinct()

        return Subject.objects.filter(
            id__in=accessible_subject_ids
        ).distinct()

    serializer_class = TechnicalLeadSubjectSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 6. CLASS SUBJECT AND TEACHER ASSIGNMENTS
# --------------------------------------------------

class TechnicalLeadClassSubjectAssignmentViewSet(
    viewsets.ModelViewSet
):

    # queryset = ClassSubjectAssignment.objects.select_related(
    #     "school_class",
    #     "subject",
    #     "teacher",
    # ).all()

    def get_queryset(self):

        team_employee_ids = get_technical_lead_team(
            self.request.user
        ).values_list(
            "id",
            flat=True
        )

        return ClassSubjectAssignment.objects.filter(
            teacher_id__in=team_employee_ids
        ).select_related(
            "school_class",
            "subject",
            "teacher"
        )

    serializer_class = TechnicalLeadClassSubjectAssignmentSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS

    def perform_create(self, serializer):

        teacher = serializer.validated_data.get("teacher")

        self.validate_teacher_access(teacher)

        serializer.save()

    def perform_update(self, serializer):

        teacher = serializer.validated_data.get(
            "teacher",
            self.get_object().teacher
        )

        self.validate_teacher_access(teacher)

        serializer.save()

    # def validate_teacher_access(self, teacher):

    #     if teacher is None:
    #         return

    #     user = self.request.user

    #     # Superusers can assign any employee as a teacher.
    #     if user.is_superuser:
    #         return

    #     technical_lead = get_technical_lead_profile(user)

    #     if technical_lead is None:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied(
    #             "Your account is not linked to an employee profile."
    #         )

    #     if teacher.reporting_manager_id != technical_lead.id:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied(
    #             "You can only assign employees from your own team as teachers."
    #         )

    def validate_class_access(self, school_class):

        class_ids = get_technical_lead_class_ids(
            self.request.user
        )

        if not SchoolClass.objects.filter(
            id__in=class_ids,
            id=school_class.id
        ).exists():

            raise PermissionDenied(
                "You cannot manage assignments for this class."
            )



class TechnicalLeadStudentAttendanceViewSet(viewsets.ModelViewSet):

    serializer_class = TechnicalLeadStudentAttendanceSerializer
    permission_classes = TECHNICAL_LEAD_PERMISSIONS

    def get_accessible_class_ids(self):

        user = self.request.user

        # Superuser can access all classes
        if user.is_superuser:
            return None

        # Get the Technical Lead's employee profile
        try:
            technical_lead = user.employee_profile
        except Employee.DoesNotExist:
            return []

        # Get employees reporting to this Technical Lead
        team_employee_ids = Employee.objects.filter(
            reporting_manager=technical_lead
        ).values_list("id", flat=True)

        # Get classes assigned to those employees
        class_ids = ClassSubjectAssignment.objects.filter(
            teacher_id__in=team_employee_ids
        ).values_list("school_class_id", flat=True).distinct()

        return class_ids

    def get_queryset(self):

        class_ids = self.get_accessible_class_ids()

        queryset = StudentAttendance.objects.select_related(
            "student",
            "school_class",
            "recorded_by"
        )

        if class_ids is None:
            return queryset

        return queryset.filter(
            school_class_id__in=class_ids
        )

    def perform_create(self, serializer):

        class_ids = self.get_accessible_class_ids()

        school_class = serializer.validated_data["school_class"]

        # Check whether this Technical Lead can access the class
        if (
            class_ids is not None
            and school_class.id not in class_ids
        ):
            raise PermissionDenied(
                "You cannot record attendance for this class."
            )

        serializer.save(
            recorded_by=self.request.user
        )

def get_technical_lead_team(user):

    if user.is_superuser:
        return Employee.objects.all()

    try:
        technical_lead = user.employee_profile
    except Employee.DoesNotExist:
        return Employee.objects.none()

    return Employee.objects.filter(
        reporting_manager=technical_lead
    )


def get_technical_lead_class_ids(user):

    if user.is_superuser:
        return SchoolClass.objects.values_list(
            "id",
            flat=True
        )

    team_employee_ids = get_technical_lead_team(
        user
    ).values_list("id", flat=True)

    return ClassSubjectAssignment.objects.filter(
        teacher_id__in=team_employee_ids
    ).values_list(
        "school_class_id",
        flat=True
    ).distinct()


class TechnicalLeadDashboardOverviewAPIView(APIView):

    permission_classes = TECHNICAL_LEAD_PERMISSIONS

    def get(self, request):

        today = timezone.localdate()

        # Employees reporting to this Technical Lead
        team = get_technical_lead_team(request.user)

        # Classes assigned to the Technical Lead's team
        class_ids = get_technical_lead_class_ids(
            request.user
        )

        # Active students enrolled in those classes
        enrollments = StudentEnrollment.objects.filter(
            school_class_id__in=class_ids,
            status="active"
        )

        student_ids = enrollments.values_list(
            "student_id",
            flat=True
        ).distinct()

        # Today's student attendance
        today_attendance = StudentAttendance.objects.filter(
            school_class_id__in=class_ids,
            date=today
        )

        attendance_summary = today_attendance.values(
            "status"
        ).annotate(
            total=Count("id")
        )

        attendance_counts = {
            "present": 0,
            "absent": 0,
            "late": 0,
            "excused": 0,
        }

        for item in attendance_summary:
            attendance_counts[item["status"]] = item["total"]

        data = {
            "total_employees": team.count(),

            "total_students": Student.objects.filter(
                id__in=student_ids
            ).distinct().count(),

            "total_classes": len(set(class_ids)),

            "total_attendance_today": today_attendance.count(),

            "attendance_today": attendance_counts,

            "date": str(today),
        }

        return Response(data)


class TechnicalLeadReportsAPIView(APIView):

    permission_classes = TECHNICAL_LEAD_PERMISSIONS

    def get(self, request):

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        class_id = request.query_params.get("class_id")
        status = request.query_params.get("status")

        class_ids = get_technical_lead_class_ids(
            request.user
        )

        attendance = StudentAttendance.objects.filter(
            school_class_id__in=class_ids
        ).select_related(
            "student",
            "school_class"
        )

        # Date filtering
        if from_date:
            attendance = attendance.filter(
                date__gte=from_date
            )

        if to_date:
            attendance = attendance.filter(
                date__lte=to_date
            )

        # Class filtering
        if class_id:
            attendance = attendance.filter(
                school_class_id=class_id
            )

        # Status filtering
        if status:
            valid_statuses = [
                "present",
                "absent",
                "late",
                "excused",
            ]

            if status not in valid_statuses:
                return Response(
                    {"error": "Invalid attendance status."},
                    status=400
                )

            attendance = attendance.filter(
                status=status
            )

        # Overall attendance summary
        summary = attendance.values(
            "status"
        ).annotate(
            total=Count("id")
        )

        summary_data = {
            "present": 0,
            "absent": 0,
            "late": 0,
            "excused": 0,
        }

        for item in summary:
            summary_data[item["status"]] = item["total"]

        # Student-wise attendance details
        records = [
            {
                "student_id": record.student.id,
                "student_name": record.student.name,
                "class_id": record.school_class.id,
                "class_name": record.school_class.name,
                "date": str(record.date),
                "status": record.status,
                "remarks": record.remarks,
            }
            for record in attendance.order_by("-date")
        ]

        return Response({
            "filters": {
                "from_date": from_date,
                "to_date": to_date,
                "class_id": class_id,
                "status": status,
            },
            "total_records": attendance.count(),
            "attendance_summary": summary_data,
            "student_attendance": records,
        })
