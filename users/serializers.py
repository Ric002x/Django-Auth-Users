from django.conf import settings
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'avatar', "name", "username", "email", "last_access"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = f"{settings.CURRENT_URL}{instance.avatar}"
        return data
