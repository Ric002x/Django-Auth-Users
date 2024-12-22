import re
from collections import defaultdict

from django.core.exceptions import ValidationError

from users.models import User


class RegisterUserValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.execute_clean()

    def strong_password(self, password):
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[1-9]).{8,}$')

        if not regex.match(password):
            self.errors['password'].append(self.ErrorClass(
                'A senha deve contar pelo menos 8 caracteres, '
                'incluindo letras maiúsculas e números',
                code='invalid',
            ))

    def execute_clean(self, *args, **kwargs):
        self.clean_email()
        self.clean_password()

        for key, value in self.data.items():
            if key != "avatar" and not self.data.get(key):
                self.errors[key].append(self.ErrorClass(
                    "Este campo é obrigatório"
                ))

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_email(self, *args, **kwargs):
        email = self.data.get('email')

        if User.objects.filter(email=email).exists():
            self.errors['email'].append(self.ErrorClass(
                "Já existe um usuário cadastrado para esse email"
            ))

    def clean_password(self, *args, **kwargs):
        password = self.data.get('password')
        password2 = self.data.get('password2')

        self.strong_password(password)

        if password != password2:
            self.errors['password'].append(self.ErrorClass(
                "As senhas não coincidem"
            ))


class LoginUserValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass

    def execute_clean(self, *args, **kwargs):
        for key, value in self.data.items():
            if not self.data[key]:
                self.errors[key].append(self.ErrorClass(
                    "Preencha este campo"
                ))

        if self.errors:
            raise self.ErrorClass(
                self.errors  # type: ignore
            )


class UpdateUserValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.execute_clean()

    def execute_clean(self, *args, **kwargs):
        self.clean_email()
        self.clean_avatar()

        for key, value in self.data.items():
            if key != "avatar" and not self.data.get(key):
                self.errors[key].append(self.ErrorClass(
                    "Este campo é obrigatório"
                ))

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_email(self, *args, **kwargs):
        email = self.data.get('email')
        user_id = self.data.get('id')

        existing_user = User.objects.filter(
            email=email).exclude(id=user_id).first()
        if existing_user:
            self.errors['email'].append(self.ErrorClass(
                "Já existe um usuário cadastrado para esse email"
            ))

    def clean_avatar(self, *args, **kwargs):
        avatar = self.data.get('avatar')

        if avatar:
            size = avatar.size
            content_type = avatar.content_type

            if content_type not in ["image/png", "image/jpeg"]:
                self.errors['avatar'].append(self.ErrorClass(
                    "Somente arquivos do tipo PNG e JPEG são suportados"
                ))

            if size > 10485760:
                self.errors['avatar'].append(self.ErrorClass(
                    "O limite máximo de tamanho de arquivo é de 10MB"
                ))


class UpdatePasswordValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.execute_clean()

    def strong_password(self, password):
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[1-9]).{8,}$')

        if not regex.match(password):
            self.errors['new_password'].append(self.ErrorClass(
                'A senha deve contar pelo menos 8 caracteres, '
                'incluindo letras maiúsculas e números',
                code='invalid',
            ))

    def execute_clean(self, *args, **kwargs):
        self.clean_password()

        for key, value in self.data.items():
            if not self.data.get(key):
                self.errors[key].append(self.ErrorClass(
                    "Este campo é obrigatório"
                ))

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_password(self, *args, **kwargs):
        new_password = self.data.get('new_password')
        repeat_password = self.data.get('repeat_password')

        self.strong_password(new_password)

        if new_password != repeat_password:
            self.errors['new_password'].append(self.ErrorClass(
                "As senhas não coincidem"
            ))
