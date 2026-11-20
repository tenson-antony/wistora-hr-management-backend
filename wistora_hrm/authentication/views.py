
from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserManagementSerializer,
)

from .permissions import IsAdminRole


User = get_user_model()


# --------------------------------------------------
# 1. LOGIN API
# --------------------------------------------------

class LoginAPIView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


# --------------------------------------------------
# 2. TOKEN REFRESH API
# --------------------------------------------------

class CustomTokenRefreshAPIView(TokenRefreshView):
    """
    Generates a new access token using a refresh token.
    """
    pass


# --------------------------------------------------
# 3. LOGOUT API
# --------------------------------------------------

class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "error": "Refresh token is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(refresh_token)

            # Prevent users from blacklisting another
            # user's refresh token.
            if token["user_id"] != request.user.id:
                return Response(
                    {
                        "error": "This refresh token does not belong to you."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            token.blacklist()

            return Response(
                {
                    "message": "Successfully logged out."
                },
                status=status.HTTP_200_OK
            )

        except TokenError:

            return Response(
                {
                    "error": "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# --------------------------------------------------
# 4. USER PROFILE API
# --------------------------------------------------

class UserProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(
            request.user
        )

        return Response(serializer.data)

    def patch(self, request):

        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        # All profile fields are read-only.
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


# --------------------------------------------------
# 5. CHANGE PASSWORD API
# --------------------------------------------------

class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        request.user.set_password(
            serializer.validated_data["new_password"]
        )

        request.user.save()

        return Response(
            {
                "message": "Password changed successfully. Please log in again."
            },
            status=status.HTTP_200_OK
        )


# --------------------------------------------------
# 6. ADMIN USER MANAGEMENT API
# --------------------------------------------------

class UserManagementViewSet(viewsets.ModelViewSet):

    queryset = User.objects.prefetch_related(
        "groups"
    ).all()

    serializer_class = UserManagementSerializer

    permission_classes = [IsAuthenticated, IsAdminRole]

    def perform_destroy(self, instance):

        if instance.id == self.request.user.id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "You cannot delete your own account."
            )

        instance.delete()

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):

        user = self.get_object()

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({
            "message": "User account activated."
        })

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):

        user = self.get_object()

        if user.id == request.user.id:
            return Response(
                {
                    "error": "You cannot deactivate your own account."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response({
            "message": "User account deactivated."
        })
