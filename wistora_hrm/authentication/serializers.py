
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from admin_dashboard.models import Employee


User = get_user_model()

# The only roles that can be assigned through this API.
ROLE_DASHBOARDS = {
    "Admin": "admin",
    "HR": "hr",
    "Technical Lead": "technical-lead",
}


# --------------------------------------------------
# HELPER: GET USER ROLE
# --------------------------------------------------

def get_user_role(user):

    if user.is_superuser:
        return "Admin"

    roles = list(
        user.groups.filter(
            name__in=ROLE_DASHBOARDS.keys()
        ).values_list("name", flat=True)
    )

    if len(roles) == 1:
        return roles[0]

    return None


# --------------------------------------------------
# 1. LOGIN SERIALIZER
# --------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        role = get_user_role(user)

        if role:
            token["role"] = role
            token["dashboard"] = ROLE_DASHBOARDS[role]

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        user = self.user

        role = get_user_role(user)

        if role is None:
            raise serializers.ValidationError(
                "Your account does not have a valid role. Contact the administrator."
            )

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role,
            "dashboard": ROLE_DASHBOARDS[role],
        }

        return data


# --------------------------------------------------
# 2. USER PROFILE SERIALIZER
# --------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField()

    employee_id = serializers.SerializerMethodField()

    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "employee_id",
            "employee_name",
        ]

        read_only_fields = fields

    def get_role(self, obj):
        return get_user_role(obj)

    def get_employee_id(self, obj):

        try:
            return obj.employee_profile.employee_id
        except Employee.DoesNotExist:
            return None

    def get_employee_name(self, obj):

        try:
            return obj.employee_profile.name
        except Employee.DoesNotExist:
            return None


# --------------------------------------------------
# 3. CHANGE PASSWORD SERIALIZER
# --------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        write_only=True,
        required=True
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate_old_password(self, value):

        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your current password is incorrect."
            )

        return value

    def validate(self, data):

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "The new passwords do not match."
            })

        from django.contrib.auth.password_validation import validate_password

        validate_password(
            data["new_password"],
            self.context["request"].user
        )

        return data


# --------------------------------------------------
# 4. ADMIN USER MANAGEMENT SERIALIZER
# --------------------------------------------------

class UserManagementSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )

    role = serializers.ChoiceField(
        choices=[
            ("Admin", "Admin"),
            ("HR", "HR"),
            ("Technical Lead", "Technical Lead"),
        ],
        write_only=True,
        required=True
    )

    assigned_role = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "assigned_role",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "assigned_role",
        ]

    def get_assigned_role(self, obj):
        return get_user_role(obj)

    def create(self, validated_data):

        password = validated_data.pop("password", None)
        role = validated_data.pop("role")

        if not password:
            raise serializers.ValidationError({
                "password": "Password is required when creating a user."
            })

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        group = Group.objects.get(name=role)

        user.groups.set([group])

        return user

    def update(self, instance, validated_data):

        password = validated_data.pop("password", None)
        role = validated_data.pop("role", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        if role:
            group = Group.objects.get(name=role)
            instance.groups.set([group])

        return instance
