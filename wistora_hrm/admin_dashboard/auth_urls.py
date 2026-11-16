from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .auth_views import (
    LoginAPIView,
    UserRegistrationAPIView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    LogoutAPIView,
)


urlpatterns = [

    # Login
    path(
        'login/',
        LoginAPIView.as_view(),
        name='login'
    ),

    # Refresh access token
    path(
        'refresh/',
        TokenRefreshView.as_view(),
        name='token-refresh'
    ),

    # Verify token
    path(
        'verify/',
        TokenVerifyView.as_view(),
        name='token-verify'
    ),

    # Register user (admin only)
    path(
        'register/',
        UserRegistrationAPIView.as_view(),
        name='register'
    ),

    # Current logged-in user
    path(
        'profile/',
        UserProfileAPIView.as_view(),
        name='profile'
    ),

    # Change password
    path(
        'change-password/',
        ChangePasswordAPIView.as_view(),
        name='change-password'
    ),

    # Logout
    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='logout'
    ),

]