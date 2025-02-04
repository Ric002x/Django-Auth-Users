import uuid
from random import randint

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer
from users.validators import (LoginUserValidator, RegisterUserValidator,
                              UpdatePasswordValidator, UpdateUserValidator)


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

        username = str(data.get('name')).split(
            ' ')[0] + str(randint(1000000, 9999999))

        user = User(
            name=data.get('name'),
            email=data.get('email'),
            username=username
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


class UserAPIView(APIView):
    def get(self, request):
        User.objects.filter(id=request.user.id).update(last_access=now())

        user = UserSerializer(request.user).data

        return Response({
            "user": user
        })

    def put(self, request):
        avatar = request.FILES.get('avatar')
        data = {
            "id": request.user.id,
            "name": request.data.get('name', ''),
            "email": request.data.get('email', ''),
            "username": request.data.get('username', ''),
            "avatar": avatar
        }

        UpdateUserValidator(data, ErrorClass=ValidationError)

        if avatar:
            storage = FileSystemStorage(
                settings.MEDIA_ROOT / "users/avatars",
                settings.MEDIA_URL + "users/avatars"
            )

            extension = avatar.name.split('.')[-1]
            file = storage.save(f"{uuid.uuid4()}.{extension}", avatar)
            avatar = storage.url(file)

        serializer = UserSerializer(request.user, data={
            "name": data.get('name'),
            "email": data.get('email'),
            "username": data.get('username'),
            "avatar": avatar or request.user.avatar,
        })

        if not serializer.is_valid():
            if avatar:
                storage.delete(avatar.split("/")[-1])
            first_error = list(
                serializer.errors.values()  # type: ignore
            )[0][0]

            raise ValidationError(first_error)

        if avatar and request.user.avatar != \
                "/media/users/avatars/default_avatar.png":
            storage.delete(request.user.avatar.split("/")[-1])

        serializer.save()

        return Response({
            "user": serializer.data
        })


class UserChangePasswordAPIView(APIView):
    def put(self, request):
        data = {
            "old_password": request.data.get('old_password'),
            "new_password": request.data.get('new_password'),
            "repeat_password": request.data.get('repeat_password'),
        }

        UpdatePasswordValidator(data, ErrorClass=ValidationError)

        user = request.user

        if user and check_password(data.get('old_password'), user.password):
            user.set_password(data.get('new_password'))
            user.save()

            return Response({
                "success": True
            })

        raise ValidationError({
            "old_password": "Senha incorreta"
        })


# OAuth Views

class OAuthLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data: dict = request.data

        user = User.objects.filter(email=data.get('email')).first()

        if not user:
            user = User(
                name=data.get('name'),
                email=data.get('email'),
                avatar=data.get('picture'),
            )
            user.save()

        user_serializer = UserSerializer(user).data
        access_token = RefreshToken.for_user(
            user
        ).access_token  # type: ignore

        return Response({
            "user": user_serializer,
            "access_token": str(access_token)
        })
