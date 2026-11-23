
from rest_framework import serializers

# Import shared serializers from Admin Dashboard
from admin_dashboard.serializers import (
    DepartmentSerializer,
    DesignationSerializer,
    EmployeeSerializer,
)

# Import shared models
from admin_dashboard.models import (
    LeaveRequest,
    AttendanceRecord,
)


# =====================================================
# 1. HR LEAVE REQUEST SERIALIZER
# =====================================================

class HRLeaveRequestSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source='employee.name',
        read_only=True
    )

    employee_id = serializers.CharField(
        source='employee.employee_id',
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

        # HR must use the approval/rejection API actions.
        read_only_fields = (
            'status',
            'reviewed_by',
            'reviewed_at',
            'created_at',
        )

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
            raise serializers.ValidationError({
                'end_date': 'End date cannot be before start date.'
            })

        return data


# =====================================================
# 2. HR ATTENDANCE SERIALIZER
# =====================================================

class HRAttendanceRecordSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source='employee.name',
        read_only=True
    )

    employee_id = serializers.CharField(
        source='employee.employee_id',
        read_only=True
    )

    department_name = serializers.CharField(
        source='employee.department.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = AttendanceRecord

        fields = '__all__'

        read_only_fields = ('created_at',)

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
            raise serializers.ValidationError({
                'check_out': 'Check-out cannot be earlier than check-in.'
            })

        return data
