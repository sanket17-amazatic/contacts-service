"""
Permission for User access
"""
from rest_framework import permissions

class IsListAction(permissions.BasePermission):
    """
    Custom User permission class.
    Check if action is list action
    """
    message = "Fetching user list is not allowed"
    
    def has_permission(self, request, view):
        """
        Method check requested user is owner or member of group
        """
        return view.action != 'list'
            
