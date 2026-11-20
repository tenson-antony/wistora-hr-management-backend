
from rest_framework import serializers

from admin_dashboard.models import (
    Employee,
    Student,
    StudentEnrollment,
    SchoolClass,
    Subject,
    ClassSubjectAssignment,
    AttendanceRecord,
    StudentAttendance,
)


# --------------------------------------------------
# 1. EMPLOYEE MANAGEMENT
# --------------------------------------------------

class TechnicalLeadEmployeeSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        allow_null=True
    )

    designation_name = serializers.CharField(
        source="designation.name",
        read_only=True,
        allow_null=True
    )

    reporting_manager_name = serializers.CharField(
        source="reporting_manager.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Employee

        fields = [
            "id",
            "employee_id",
            "name",
            "email",
            "phone",
            "department",
            "department_name",
            "designation",
            "designation_name",
            "joining_date",
            "status",
            "reporting_manager",
            "reporting_manager_name",
            "created_at",
            "updated_at",
        ]

        # Technical Leads can view employee information,
        # but cannot change employee records.
        read_only_fields = fields


# --------------------------------------------------
# 2. STUDENT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


# --------------------------------------------------
# 3. STUDENT ENROLLMENT
# --------------------------------------------------

class TechnicalLeadStudentEnrollmentSerializer(
    serializers.ModelSerializer
):

    student_name = serializers.CharField(
        source="student.name",
        read_only=True
    )

    class_name = serializers.CharField(
        source="school_class.name",
        read_only=True
    )

    academic_session_name = serializers.CharField(
        source="school_class.academic_session.name",
        read_only=True
    )

    class Meta:
        model = StudentEnrollment

        fields = "__all__"

        read_only_fields = ("id", "created_at")


# --------------------------------------------------
# 4. CLASS MANAGEMENT
# --------------------------------------------------

class TechnicalLeadClassSerializer(serializers.ModelSerializer):

    academic_session_name = serializers.CharField(
        source="academic_session.name",
        read_only=True
    )

    class Meta:
        model = SchoolClass

        fields = "__all__"

        read_only_fields = ("id", "created_at")


# --------------------------------------------------
# 5. SUBJECT MANAGEMENT
# --------------------------------------------------

class TechnicalLeadSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject

        fields = "__all__"


# --------------------------------------------------
# 6. CLASS SUBJECT ASSIGNMENT
# --------------------------------------------------

class TechnicalLeadClassSubjectAssignmentSerializer(
    serializers.ModelSerializer
):

    class_name = serializers.CharField(
        source="school_class.name",
        read_only=True
    )

    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True
    )

    teacher_name = serializers.CharField(
        source="teacher.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ClassSubjectAssignment

        fields = "__all__"

        read_only_fields = ("id", "assigned_at")


# --------------------------------------------------
# 7. STUDENT ATTENDANCE
# --------------------------------------------------


class TechnicalLeadStudentAttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.name",
        read_only=True
    )

    class_name = serializers.CharField(
        source="school_class.name",
        read_only=True
    )

    recorded_by_name = serializers.CharField(
        source="recorded_by.username",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = StudentAttendance

        fields = [
            "id",
            "student",
            "student_name",
            "school_class",
            "class_name",
            "date",
            "status",
            "remarks",
            "recorded_by",
            "recorded_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "recorded_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        # Get student and class during creation or update
        student = attrs.get(
            "student",
            getattr(self.instance, "student", None)
        )

        school_class = attrs.get(
            "school_class",
            getattr(self.instance, "school_class", None)
        )

        # Ensure student and class are provided
        if not student or not school_class:
            raise serializers.ValidationError(
                "Student and class are required."
            )

        # Check whether the student is actively enrolled
        enrollment_exists = StudentEnrollment.objects.filter(
            student=student,
            school_class=school_class,
            status="active"
        ).exists()

        if not enrollment_exists:
            raise serializers.ValidationError({
                "student": (
                    "This student is not actively enrolled "
                    "in the selected class."
                )
            })

        return attrs
