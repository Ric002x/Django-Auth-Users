from django import forms

from users.validators import UpdatePasswordValidator


class UpdatePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Senha antiga"
        })
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Nova senha"
        })
    )

    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repetir senha"
        })
    )

    def clean(self, *args, **kwargs):
        super_clean = super().clean(*args, **kwargs)
        UpdatePasswordValidator(self.cleaned_data)
        return super_clean
