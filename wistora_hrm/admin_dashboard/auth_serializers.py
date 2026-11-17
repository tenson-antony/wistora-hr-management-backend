
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Employee


User = get_user_model()


# =====================================================
# 1. CUSTOM LOGIN SERIALIZER
# =====================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        token['is_staff'] = user.is_staff

        token['groups'] = list(
            user.groups.values_list('name', flat=True)
        )

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        user = self.user

        employee = getattr(
            user,
            'employee_profile',
            None
        )

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'groups': list(
                user.groups.values_list('name', flat=True)
            ),
            'employee_id': (
                employee.employee_id if employee else None
            ),
            'employee_name': (
                employee.name if employee else None
            ),
        }

        return data


# =====================================================
# 2. USER REGISTRATION SERIALIZER
# =====================================================

class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(user__isnull=True),
        required=False,
        allow_null=True
    )

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
            'employee',
        ]

        read_only_fields = ['id']

    def validate(self, data):

        if data['password'] != data['password_confirm']:

            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        return data

    def create(self, validated_data):

        validated_data.pop('password_confirm')

        employee = validated_data.pop('employee', None)

        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            is_staff=False,
            is_superuser=False,
            **validated_data
        )

        if employee:

            employee.user = user

            employee.save(update_fields=['user'])

        return user


# =====================================================
# 3. USER PROFILE SERIALIZER
# =====================================================

class UserProfileSerializer(serializers.ModelSerializer):

    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    employee_id = serializers.SerializerMethodField()

    employee_name = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'groups',
            'employee_id',
            'employee_name',
        ]

        read_only_fields = fields

    def get_employee_id(self, obj):

        employee = getattr(
            obj,
            'employee_profile',
            None
        )

        return employee.employee_id if employee else None

    def get_employee_name(self, obj):

        employee = getattr(
            obj,
            'employee_profile',
            None
        )

        return employee.name if employee else None


# =====================================================
# 4. CHANGE PASSWORD SERIALIZER
# =====================================================

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_old_password(self, value):

        user = self.context['request'].user

        if not user.check_password(value):

            raise serializers.ValidationError(
                'Current password is incorrect.'
            )

        return value

    def validate(self, data):

        if data['new_password'] != data['confirm_password']:

            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        if data['old_password'] == data['new_password']:

            raise serializers.ValidationError({
                'new_password': 'New password must be different.'
            })

        return data

    def save(self, **kwargs):

        user = self.context['request'].user

        user.set_password(
            self.validated_data['new_password']
        )

        user.save(update_fields=['password'])

        return user
