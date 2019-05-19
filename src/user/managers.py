"""
Custom user manager for creating custom user
"""
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where phone is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, phone, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not phone:
            raise ValueError('The Phone number must be set')
        if not extra_fields.get('name') :
            raise ValueError('Name is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone and password.
        """
        extra_fields.setdefault('is_otp_verified', True)

        if extra_fields.get('is_otp_verified') is not True:
            raise ValueError('Superuser must have is_otp_verified=True.')
        return self.create_user(phone, password, **extra_fields)
