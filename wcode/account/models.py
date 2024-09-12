from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
import re
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    age = models.PositiveIntegerField(null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    password_history = models.JSONField(default=list, blank=True)  # To store password history
    chatroomID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique ID for chat room

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number', 'age', 'sex']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        if self.password_history and make_password(raw_password) in self.password_history:
            raise ValidationError("You cannot use your previous password.")
        super().set_password(raw_password)
        self.password_history.append(make_password(raw_password))
        if len(self.password_history) > 5:  # Keep history for last 5 passwords
            self.password_history.pop(0)
        self.save()
