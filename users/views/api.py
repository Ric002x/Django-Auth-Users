from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer
from users.validators import LoginUserValidator, RegisterUserValidator


class CreateUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {
            "name": request.data.get('name', ''),
            "email": request.data.get('email', ''),
            "password": request.data.get('password', ''),
            "repeat_password": request.data.get('repeat_password', ''),
        }
        RegisterUserValidator(data, ErrorClass=ValidationError)

        user = User(
            name=data.get('name'),
            email=data.get('email')
        )
        user.set_password(data.get('password'))
        user.save()

        user_serializer = UserSerializer(user).data
        access_token = RefreshToken.for_user(
            user
        ).access_token  # type: ignore

        return Response({
            "user": user_serializer,
            "access_token": str(access_token)
        })


class LoginUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {
            "email": request.data.get('email', ""),
            "password": request.data.get('password', "")
        }
        LoginUserValidator(data, ErrorClass=ValidationError)

        user = User.objects.filter(email=data.get('email')).first()
        if not user or not check_password(data.get('password'), user.password):
            raise AuthenticationFailed

        user_serializer = UserSerializer(user).data
        access_token = RefreshToken.for_user(
            user
        ).access_token  # type: ignore

        return Response({
            "user": user_serializer,
            "access_token": str(access_token)
        })
