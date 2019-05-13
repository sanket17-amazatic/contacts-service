"""
Models for creatin user profile of the contact project application
"""
import phonenumbers
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from core.models import SoftDeletionModel 
from .managers import CustomUserManager


def is_phone_number_valid(number):
    """
    Custom validation for phone number field
    """
    try:
        phone_number = phonenumbers.parse(number, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError('Invalid phone number, numerical values are accepted only')
    if not phonenumbers.is_valid_number(phone_number):
         raise ValidationError('Invalid phone number')

class User(SoftDeletionModel, AbstractBaseUser):
    """
    Custom user profile class
    """
    phone = models.CharField(max_length=15, unique=True, validators=[is_phone_number_valid])
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    objects = CustomUserManager()

    def __str__(self):
        """
        String represntation of app user
        """
        return self.phone

class BlackListedToken(models.Model):
    """
    Model for black listing token
    """
    token = models.CharField(max_length=500)
    user = models.ForeignKey(User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")

    def __str__(self):
        """
        String representation of black listed token
        """
        return self.token
