
from rest_framework import serializers

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


# =====================================================
# 1. DEPARTMENT SERIALIZER
# =====================================================

class DepartmentSerializer(serializers.ModelSerializer):

    department_head_name = serializers.CharField(
        source='department_head.name',
        read_only=True
    )

    class Meta:
        model = Department

        fields = '__all__'

        read_only_fields = ['created_at']


# =====================================================
# 2. DESIGNATION SERIALIZER
# =====================================================

class DesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation

        fields = '__all__'


# =====================================================
# 3. EMPLOYEE SERIALIZER
# =====================================================

class EmployeeSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )

    designation_name = serializers.CharField(
        source='designation.name',
        read_only=True
    )

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Employee

        fields = '__all__'

        read_only_fields = [
            'created_at',
            'updated_at'
        ]


# =====================================================
# 4. ACADEMIC SESSION SERIALIZER
# =====================================================

class AcademicSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicSession

        fields = '__all__'

        read_only_fields = ['created_at']

    def validate(self, data):

        start_date = data.get(
            'start_date',
            getattr(self.instance, 'start_date', None)
        )

        end_date = data.get(
            'end_date',
            getattr(self.instance, 'end_date', None)
        )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                "End date must be after start date."
            )

        return data


# =====================================================
# 5. SUBJECT SERIALIZER
# =====================================================

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject

        fields = '__all__'


# =====================================================
# 6. SCHOOL CLASS SERIALIZER
# =====================================================

class SchoolClassSerializer(serializers.ModelSerializer):

    academic_session_name = serializers.CharField(
        source='academic_session.name',
        read_only=True
    )

    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = SchoolClass

        fields = '__all__'

        read_only_fields = ['created_at']


# =====================================================
# 7. CLASS SUBJECT ASSIGNMENT SERIALIZER
# =====================================================

class ClassSubjectAssignmentSerializer(serializers.ModelSerializer):

    class_name = serializers.CharField(
        source='school_class.name',
        read_only=True
    )

    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )

    teacher_name = serializers.CharField(
        source='teacher.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ClassSubjectAssignment

        fields = '__all__'

        read_only_fields = ['assigned_at']


# =====================================================
# 8. STUDENT SERIALIZER
# =====================================================

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student

        fields = '__all__'

        read_only_fields = [
            'created_at',
            'updated_at'
        ]


# =====================================================
# 9. STUDENT ENROLLMENT SERIALIZER
# =====================================================

class StudentEnrollmentSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source='student.name',
        read_only=True
    )

    class_name = serializers.CharField(
        source='school_class.name',
        read_only=True
    )

    academic_session_name = serializers.CharField(
        source='school_class.academic_session.name',
        read_only=True
    )

    class Meta:
        model = StudentEnrollment

        fields = '__all__'

        read_only_fields = ['created_at']


# =====================================================
# 10. LEAVE REQUEST SERIALIZER
# =====================================================

class LeaveRequestSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source='employee.name',
        read_only=True
    )

    reviewer_name = serializers.CharField(
        source='reviewed_by.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = LeaveRequest

        fields = '__all__'

        read_only_fields = [
            'created_at',
            'reviewed_at'
        ]

    def validate(self, data):

        start_date = data.get(
            'start_date',
            getattr(self.instance, 'start_date', None)
        )

        end_date = data.get(
            'end_date',
            getattr(self.instance, 'end_date', None)
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "Leave end date cannot be before start date."
            )

        return data


# =====================================================
# 11. ATTENDANCE SERIALIZER
# =====================================================

class AttendanceRecordSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source='employee.name',
        read_only=True
    )

    class Meta:
        model = AttendanceRecord

        fields = '__all__'

        read_only_fields = ['created_at']

    def validate(self, data):

        check_in = data.get(
            'check_in',
            getattr(self.instance, 'check_in', None)
        )

        check_out = data.get(
            'check_out',
            getattr(self.instance, 'check_out', None)
        )

        if check_in and check_out and check_out < check_in:
            raise serializers.ValidationError(
                "Check-out time cannot be before check-in time."
            )

        return data


# =====================================================
# 12. SYSTEM SETTING SERIALIZER
# =====================================================

class SystemSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemSetting

        fields = '__all__'

        read_only_fields = ['updated_at']


# =====================================================
# 13. AUDIT LOG SERIALIZER
# =====================================================

class AuditLogSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = AuditLog

        fields = '__all__'

        read_only_fields = [
            'id',
            'user',
            'action',
            'module',
            'description',
            'ip_address',
            'created_at',
        ]

# =====================================================
# 14. NOTIFICATION SERIALIZER
# =====================================================

class NotificationSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='recipient.username',
        read_only=True
    )

    class Meta:
        model = Notification

        fields = '__all__'

        read_only_fields = ['created_at']
