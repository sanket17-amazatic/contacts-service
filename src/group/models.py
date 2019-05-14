"""
Model for Groups, Members, Member contact number
"""
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from core.models import SoftDeletionModel
from user.models import User

class Contact(SoftDeletionModel, models.Model):
    """
    Group Contact details
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        """
        String representation for group member 
        """
        return "{} {}".format(self.first_name, self.last_name)

class ContactNumber(SoftDeletionModel, models.Model):
    """
    Member Contact number
    """
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='contact')
    phone = PhoneNumberField(db_index=True)

    def __str__(self):
        """
        String representation of contact number
        """
        return str(self.phone)

class ContactEmail(SoftDeletionModel, models.Model):
    """
    Contact email
    """
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='email')
    email = models.EmailField()

    def __str__(self):
        """
        String representation of contact email
        """
        return self.email

class Group(SoftDeletionModel, models.Model):
    """
    Group class for app-user
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    contacts = models.ManyToManyField(Contact, blank=True, related_name='contact_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of group class
        """
        return self.name

class Member(SoftDeletionModel, models.Model):
    """
    Member for group
    """
    ADM = 'ADM'
    OWN = 'OWN'
    MEM = 'MEM'

    ROLE_TYPES = (
        (ADM, "ADMIN"),
        (OWN, "OWNER"),
        (MEM, "MEMBER"),
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_member')
    role_type = models.CharField(choices=ROLE_TYPES, max_length=10)

    def __str__(self):
        """
        String representation of member class
        """
        return str(self.user.phone)
