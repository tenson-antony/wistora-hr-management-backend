
from rest_framework.permissions import BasePermission


class IsTechnicalLeadRole(BasePermission):
    """
    Allows access only to authenticated Technical Leads.
    Superusers also have access.
    """

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(
            name="Technical Lead"
        ).exists()


class HasEmployeeProfile(BasePermission):
    """
    Ensures the Technical Lead has an Employee profile.
    """

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return hasattr(user, "employee_profile")
