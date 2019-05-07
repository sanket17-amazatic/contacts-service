"""
View for Group and group member detials
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from group.models import (Group, Contact)
from ..serializers.group_serializers import (GroupSerializer, ContactSerializer)
from ..permissions.token_permissions import IsTokenValid
from ..permissions.group_permissions import IsValidGroupUser

class GroupViewSet(viewsets.ModelViewSet):
    """
    Viewset for Group
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classess = (IsTokenValid, IsValidGroupUser)

class ContactViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining group contact
    """
    queryset = Contact.objects.all()
    permission_classess = (IsTokenValid, IsValidGroupUser)
    serializer_class = ContactSerializer
