"""
Registering group, member and member contact number
"""
from django.contrib import admin
from .models import (Group, Contact, ContactNumber, ContactEmail)

class GroupAdmin(admin.ModelAdmin):
    """
    Custom class to override default group admin method
    """
    def get_queryset(self, request):
        """
        custom queryset method to override default admin method
        """
        query_set = Group.all_objects.all()
        return query_set

class ContactAdmin(admin.ModelAdmin):
    """
    Custom class to override default contact admin method
    """
    def get_queryset(self, request):
        """
        custom queryset method to override default admin method
        """
        query_set = Contact.all_objects.all()
        return query_set

admin.site.register(Group, GroupAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactNumber)
admin.site.register(ContactEmail)
