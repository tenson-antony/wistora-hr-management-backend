
from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    """
    Base permission class for checking Django user groups.
    """

    allowed_roles = ()

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superuser has access to every dashboard.
        if user.is_superuser:
            return True

        return user.groups.filter(
            name__in=self.allowed_roles
        ).exists()


# Admin dashboard access
class IsAdminRole(RolePermission):
    allowed_roles = ('Admin',)


# HR dashboard access
class IsHRRole(RolePermission):
    allowed_roles = ('HR',)


# Technical Lead dashboard access
class IsTechnicalLeadRole(RolePermission):
    allowed_roles = ('Technical Lead',)


# Admin and HR access
class IsAdminOrHRRole(RolePermission):
    allowed_roles = ('Admin', 'HR')


# Admin and Technical Lead access
class IsAdminOrTechnicalLeadRole(RolePermission):
    allowed_roles = ('Admin', 'Technical Lead')
