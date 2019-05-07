"""
Registering AppUser, BlackListedToken model
"""
from django.contrib import admin
from user.models import (User, BlackListedToken)

class UserAdmin(admin.ModelAdmin):
    """
    Custom class to override default admin method
    """
    def get_queryset(self, request):
        """
        custom queryset method to override default admin method
        """
        qs = User.all_objects.all()
        return qs

admin.site.register(User, UserAdmin)
admin.site.register(BlackListedToken)
