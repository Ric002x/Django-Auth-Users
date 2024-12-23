import re
from collections import defaultdict

from django.core.exceptions import ValidationError

from users.models import User


class RegisterUserValidator:
    def __init__(self, data, errors=None, ErrorClass=None):
        self.data: dict = data
        self.errors = defaultdict(list) if errors is None else errors
        self.ErrorClass = ValidationError if ErrorClass is None else ErrorClass
        self.fields = ['name', 'email', 'password', 'repeat_password']
        self.execute_clean()

    def strong_password(self, password):
        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[1-9]).{8,}$')

        if not regex.match(password):
            self.errors['password'].append(
                'A senha deve contar pelo menos 8 caracteres, '
                'incluindo letras maiúsculas e números',
            )

    def execute_clean(self, *args, **kwargs):
        for field in self.fields:

            if not self.data.get(field):
                self.errors[field].append(
                    "Este campo é obrigatório"
                )

        self.clean_email()
        self.clean_password()
        self.clean_avatar()

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

    def clean_avatar(self):
        pass


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
        self.fields = ['name', 'email']
        return super().execute_clean(*args, **kwargs)

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
            self.errors['new_password'].append(
                'A senha deve contar pelo menos 8 caracteres, '
                'incluindo letras maiúsculas e números'
            )

    def execute_clean(self, *args, **kwargs):
        fields = ['old_password', 'new_password', 'repeat_password']
        for i in fields:
            if not self.data.get(i):
                self.errors[i].append(
                    "Este campo é obrigatório"
                )

        self.clean_password()

        if self.errors:
            raise self.ErrorClass(self.errors)  # type: ignore

    def clean_password(self, *args, **kwargs):
        new_password = self.data.get('new_password')
        repeat_password = self.data.get('repeat_password')

        self.strong_password(new_password)

        if new_password != repeat_password:
            self.errors['new_password'].append(
                "As senhas não coincidem"
            )
