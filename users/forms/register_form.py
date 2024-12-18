from django import forms

from users.models import User
from users.validators import RegisterUserValidator


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Repetir Senha',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password', 'password2'
        ]

        labels = {
            'name': "Nome",
            'email': "E-mail",
            'password': "Senha",
        }

    def clean(self, *args, **kwargs):
        super_clean = super().clean(*args, **kwargs)
        RegisterUserValidator(data=self.cleaned_data)
        return super_clean
