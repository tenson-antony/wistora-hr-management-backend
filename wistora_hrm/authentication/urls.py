
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginAPIView,
    LogoutAPIView,
    CustomTokenRefreshAPIView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    UserManagementViewSet,
)


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

router = DefaultRouter()

router.register(
    "users",
    UserManagementViewSet,
    basename="authentication-users"
)


# --------------------------------------------------
# URL PATTERNS
# --------------------------------------------------

urlpatterns = [

    # Login
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login"
    ),

    # Logout
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout"
    ),

    # Refresh JWT token
    path(
        "token/refresh/",
        CustomTokenRefreshAPIView.as_view(),
        name="token-refresh"
    ),

    # Logged-in user profile
    path(
        "profile/",
        UserProfileAPIView.as_view(),
        name="profile"
    ),

    # Change password
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password"
    ),

    # Admin user management
    path(
        "",
        include(router.urls)
    ),
]
