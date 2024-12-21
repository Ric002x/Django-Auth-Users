from django import forms

from users.models import User
from users.validators import RegisterUserValidator


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Senha"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repitir sua Senha"
        })
    )

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password', 'password2'
        ]

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nome"}),
            "email": forms.EmailInput(attrs={"placeholder": "E-mail"}),
        }

    def clean(self, *args, **kwargs):
        super_clean = super().clean(*args, **kwargs)
        RegisterUserValidator(data=self.cleaned_data)
        return super_clean
