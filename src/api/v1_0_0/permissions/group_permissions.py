"""
Permission for group access
"""
from rest_framework import permissions
from group.models import (Member, Group)

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
        valid_user = None
        if 'members' in request.get_full_path():
            group = Member.objects.filter(id=view.kwargs.get('pk')).values('group').first()
            valid_user = Member.objects.filter(user=request.user, group=group['group']).first()
        elif 'groups' in request.get_full_path():
            valid_user = Member.objects.filter(user=request.user, group=view.kwargs.get('pk')).first()
        elif 'contacts' in request.get_full_path():
            group = Group.objects.filter(contacts__id=view.kwargs.get('pk')).first()
            valid_user = Member.objects.filter(user=request.user, group=group).first()   
        if valid_user is None:
            return False
        if valid_user.role_type == 'member':
            return False
        return True
