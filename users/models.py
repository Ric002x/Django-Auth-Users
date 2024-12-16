from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_superuser(self, email, password):
        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    avatar = models.TextField(default='/media/avatars/default_avatar.png')
    is_superuser = models.BooleanField(default=False)
    last_access = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def has_perm(self, perm, object=None):
        return True

    def has_module_perms(self, app_Label):
        return True

    @property
    def is_staff(self):
        return self.is_superuser
