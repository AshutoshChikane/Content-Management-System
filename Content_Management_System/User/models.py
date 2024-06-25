from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
import re


def validate_pincode(value):
    """This function is used to validation of pincode"""
    if value < 100000 or value > 999999:
        raise ValidationError(
            '%(value)s is not a valid pincode. A pincode must be a 6 digit number.',
            params={'value': value},
        )


def validate_phone(value):
    if value < 1000000000 or value > 9999999999:
        raise ValidationError(
            '%(value)s is not a valid phone number. A phone must be a 10 digit number.',
            params={'value': value},
        )


def validate_full_name(value):
    words = value.split()
    if len(words) != 2:
        raise ValidationError('Full name must consist of exactly two words.', code='invalid_full_name')

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    full_name = models.CharField(max_length=150, blank=False, verbose_name='Full Name', validators=[validate_full_name])
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    address = models.CharField(max_length=300, blank=True, default="")
    phone = models.PositiveIntegerField(validators=[validate_phone], blank=False, default=0, unique=True)
    pincode = models.PositiveIntegerField(validators=[validate_pincode], blank=False, default=0)
    country = models.CharField(max_length=100, blank=True, default="")

    objects = CustomUserManager()  # Assign the custom manager

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'phone', 'pincode']

    def clean(self):
        super().clean()
        if self.password:
            if len(self.password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if not re.search(r'[A-Z]', self.password):
                raise ValidationError('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', self.password):
                raise ValidationError('Password must contain at least one lowercase letter.')

    def save(self, *args, **kwargs):
        if self.full_name:
            full_name_data = self.full_name.split()
            self.first_name = full_name_data[0] if len(full_name_data) > 0 else ""
            self.last_name = full_name_data[1] if len(full_name_data) > 1 else ""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username