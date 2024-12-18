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
