"""
Registering group, member and member contact number
"""
from django.contrib import admin
from groups.models import (Group, Member, MemberContactNumber)

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

class MemberAdmin(admin.ModelAdmin):
    """
    Custom class to override default member admin method
    """
    def get_queryset(self, request):
        """
        custom queryset method to override default admin method
        """
        query_set = Member.all_objects.all()
        return query_set

admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(MemberContactNumber)
