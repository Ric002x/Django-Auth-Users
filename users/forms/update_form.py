from django import forms

from users.models import User
from users.validators import UpdateUserValidator


class UpdateUserForm(forms.ModelForm):
    id = forms.CharField(
        widget=forms.HiddenInput()
    )
    email = forms.CharField(
        widget=forms.EmailInput()
    )
    avatar = forms.FileField()

    class Meta:
        model = User
        fields = ["id", "name", 'email', 'avatar']

    def clean(self, *args, **kwargs):
        UpdateUserValidator(self.data)
