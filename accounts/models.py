"""
Models for creatin user profile of the contact project application
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from contact_project.restconf.models import SoftDeletionModel 

class AppUser(SoftDeletionModel, AbstractUser):
    """
    Custom user profile class
    """
    phone = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String represntation of app user
        """
        return self.username

class BlackListedToken(models.Model):
    """
    Model for black listing token
    """
    token = models.CharField(max_length=500)
    user = models.ForeignKey(AppUser, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")

    def __str__(self):
        """
        String representation of black listed token
        """
        return self.token
