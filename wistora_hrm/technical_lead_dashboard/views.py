from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from admin_dashboard.models import (
    Employee,
    Student,
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

    def get_queryset(self):

        user = self.request.user

        # Superusers can view all employees.
        if user.is_superuser:
            return Employee.objects.select_related(
                "department",
                "designation",
                "reporting_manager",
            ).all()

        technical_lead = get_technical_lead_profile(user)

        if technical_lead is None:
            return Employee.objects.none()

        return Employee.objects.select_related(
            "department",
            "designation",
            "reporting_manager",
        ).filter(
            reporting_manager=technical_lead
        )


# --------------------------------------------------
# 2. STUDENT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadStudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.all()

    serializer_class = TechnicalLeadStudentSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 3. STUDENT ENROLLMENT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadStudentEnrollmentViewSet(
    viewsets.ModelViewSet
):

    queryset = StudentEnrollment.objects.select_related(
        "student",
        "school_class",
        "school_class__academic_session",
    ).all()

    serializer_class = TechnicalLeadStudentEnrollmentSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 4. CLASS MANAGEMENT
# --------------------------------------------------

class TechnicalLeadClassViewSet(viewsets.ModelViewSet):

    queryset = SchoolClass.objects.select_related(
        "academic_session"
    ).prefetch_related(
        "subjects"
    ).all()

    serializer_class = TechnicalLeadClassSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 5. SUBJECT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadSubjectViewSet(viewsets.ModelViewSet):

    queryset = Subject.objects.all()

    serializer_class = TechnicalLeadSubjectSerializer

    permission_classes = TECHNICAL_LEAD_PERMISSIONS


# --------------------------------------------------
# 6. CLASS SUBJECT AND TEACHER ASSIGNMENTS
# --------------------------------------------------

class TechnicalLeadClassSubjectAssignmentViewSet(
    viewsets.ModelViewSet
):

    queryset = ClassSubjectAssignment.objects.select_related(
        "school_class",
        "subject",
        "teacher",
    ).all()

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

    def validate_teacher_access(self, teacher):

        if teacher is None:
            return

        user = self.request.user

        # Superusers can assign any employee as a teacher.
        if user.is_superuser:
            return

        technical_lead = get_technical_lead_profile(user)

        if technical_lead is None:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Your account is not linked to an employee profile."
            )

        if teacher.reporting_manager_id != technical_lead.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only assign employees from your own team as teachers."
            )