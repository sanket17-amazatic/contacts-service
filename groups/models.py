"""
Model for Groups, Members, Member contact number
"""
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from contact_project.restconf.models import SoftDeletionModel
from accounts.models import AppUser

class Member(SoftDeletionModel, models.Model):
    """
    Group member details
    """
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True)
    dob = models.DateField(null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation for group member 
        """
        return self.name 

class MemberContactNumber(SoftDeletionModel, models.Model):
    """
    Member Contact number
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='contact')
    phone = PhoneNumberField(db_index=True)

    def __str__(self):
        """
        String representation of contact number
        """
        return str(self.phone)

class Group(SoftDeletionModel, models.Model):
    """
    Group class for app-user
    """
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user_groups')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    member = models.ManyToManyField(Member, blank=True, related_name='group_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of group class
        """
        return self.name
