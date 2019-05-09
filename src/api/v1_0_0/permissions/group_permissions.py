"""
Permission for group access
"""
from django.db.models import Q
from rest_framework import permissions
from group.models import (Group, Contact)

class IsValidGroupUser(permissions.BasePermission):
    """
    Custom Group permission class.
    Check if requested user is owner or member of the group
    """
    message = "You are not a owner/member of this group"
    
    def has_permission(self, request, view):
        """
        Method check requested user is owner or member of group
        """
        valid_user = Member.objects.filter(user=request.user)
        if valid_user is None:
            return False
        if valid_user.role_type != 'ADMIN' or valid_user.role_type != 'OWNER':
            return False
        return True
