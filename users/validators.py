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
            self.errors['password'].append(
                'A senha deve contar pelo menos 8 caracteres, '
                'incluindo letras maiúsculas e números',
            )

    def execute_clean(self, *args, **kwargs):
        if not self.data.get('name'):
            self.errors['name'].append(
                "Este campo é obrigatório"
            )
        if not self.data.get('email'):
            self.errors['email'].append(
                "Este campo é obrigatório"
            )
        if not self.data.get('password'):
            self.errors['password'].append(
                "Este campo é obrigatório"
            )
        if not self.data.get('repeat_password'):
            self.errors['repeat_password'].append(
                "Este campo é obrigatório"
            )

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

        self.clean_email()
        self.clean_password()

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_email(self, *args, **kwargs):
        email = self.data.get('email')

        if User.objects.filter(email=email).exists():
            self.errors['email'].append(
                "Já existe um usuário cadastrado para esse email"
            )

    def clean_password(self, *args, **kwargs):
        password = self.data.get('password')
        password2 = self.data.get('repeat_password')

        self.strong_password(password)

        if password != password2:
            self.errors['password'].append(
                "As senhas não coincidem"
            )


class LoginUserValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.execute_clean()

    def execute_clean(self, *args, **kwargs):
        email = self.data.get('email')
        password = self.data.get('password')

        if not email:
            self.errors['email'].append(
                "Preencha os campos"
            )
        if not password:
            self.errors['password'].append(
                "Preencha os campos"
            )

        if self.errors:
            raise self.ErrorClass(
                self.errors  # type: ignore
            )


class UpdateUserValidator(RegisterUserValidator):

    def execute_clean(self, *args, **kwargs):
        if not self.data.get('name'):
            self.errors['name'].append(
                "Este campo é obrigatório"
            )
        if not self.data.get('email'):
            self.errors['email'].append(
                "Este campo é obrigatório"
            )

        self.clean_email()
        self.clean_avatar()

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_email(self, *args, **kwargs):
        email = self.data.get('email')
        user_id = self.data.get('id')

        existing_user = User.objects.filter(
            email=email).exclude(id=user_id).first()
        if existing_user:
            self.errors['email'].append(
                "Já existe um usuário cadastrado para esse email"
            )

    def clean_avatar(self, *args, **kwargs):
        avatar = self.data.get('avatar')

        if avatar:
            size = avatar.size
            content_type = avatar.content_type

            if content_type not in ["image/png", "image/jpeg"]:
                self.errors['avatar'].append(
                    "Somente arquivos do tipo PNG e JPEG são suportados"
                )

            if size > 10485760:
                self.errors['avatar'].append(
                    "O limite máximo de tamanho de arquivo é de 10MB"
                )

    def clean_password(self, *args, **kwargs):
        return None


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
