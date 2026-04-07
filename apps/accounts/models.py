from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password):
        user = self.model(email=email)
        user.email = self.normalize_email(email)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("member", "MEMBER"),
    ]

    objects = CustomUserManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default="member")
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"
