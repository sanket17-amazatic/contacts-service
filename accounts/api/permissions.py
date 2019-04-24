"""
User defined permission for account application
"""
from rest_framework import permissions
from accounts.models import BlackListedToken

class IsTokenValid(permissions.BasePermission):
    """
    Class to check token validity
    """
    def has_permission(self, request, view):
        """
        Method to check input token exist in black listed token list.
        """
        user_id = request.user.id            
        is_allowed_user = True
        token = request.auth.decode("utf-8")
        try:
            is_blackListed = BlackListedToken.objects.get(user=user_id, token=token)
            if is_blackListed:
                is_allowed_user = False
        except BlackListedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user
