
from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):
    """
    Allows authenticated users.
    """

    def has_permission(self, request, view):

        return bool(
            request.user
            and request.user.is_authenticated
        )


class HasRole(BasePermission):
    """
    Base permission for checking Django Group roles.
    """

    allowed_roles = ()

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user.groups.filter(
            name__in=self.allowed_roles
        ).exists()


class IsAdminRole(HasRole):
    allowed_roles = ("Admin",)


class IsHRRole(HasRole):
    allowed_roles = ("HR",)


class IsTechnicalLeadRole(HasRole):
    allowed_roles = ("Technical Lead",)


class IsAdminOrHRRole(HasRole):
    allowed_roles = ("Admin", "HR")


class IsAdminOrTechnicalLeadRole(HasRole):
    allowed_roles = ("Admin", "Technical Lead")
