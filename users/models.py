# from django.db import models
from djongo import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    # Delete not use field
    username = None
    is_staff = None
    is_superuser = None

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    roles = models.JSONField(default=['Customer'])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'Users'


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()

    def __str__(self):
        return self.token

    class Meta:
        db_table = 'RefreshTokens'
