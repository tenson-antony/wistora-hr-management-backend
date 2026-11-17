
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .auth_serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)


User = get_user_model()


# =====================================================
# 1. LOGIN
# =====================================================

class LoginAPIView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


# =====================================================
# 2. USER REGISTRATION
# =====================================================

class UserRegistrationAPIView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = UserRegistrationSerializer

    permission_classes = [IsAuthenticated, IsAdminUser]


# =====================================================
# 3. CURRENT USER PROFILE
# =====================================================

class UserProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(
            request.user
        )

        return Response(serializer.data)


# =====================================================
# 4. CHANGE PASSWORD
# =====================================================

class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                'message': 'Password changed successfully.'
            },
            status=status.HTTP_200_OK
        )


# =====================================================
# 5. LOGOUT
# =====================================================

class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get('refresh')

        if not refresh_token:

            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(refresh_token)

            if str(token['user_id']) != str(request.user.pk):

                return Response(
                    {'error': 'Invalid refresh token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token.blacklist()

            return Response(
                {'message': 'Logged out successfully.'},
                status=status.HTTP_200_OK
            )

        except TokenError:

            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
