"""
View for Group and group member detials
"""
from django.db.models import (Q, Prefetch)
from rest_framework import viewsets
from rest_framework.decorators import action
from group.models import (Group, Contact)
from ..serializers.group_serializers import (
    GroupSerializer, ContactSerializer)
from ..permissions.token_permissions import IsTokenValid
from ..permissions.group_permissions import IsValidGroupUser


class GroupViewSet(viewsets.ModelViewSet):
    """
    Viewset for Group
    """
    serializer_class = GroupSerializer
    permission_classess = (IsTokenValid, IsValidGroupUser)

    def get_queryset(self):
        """
        Overriding queryset method 
        Fetches record according to owner and membership of a user
        """
        group_info = Group.objects.filter(
            Q(owner=self.request.user) | Q(group_members_in=[self.request.user, ]))
        return group_info


class ContactViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining group contact
    """
    permission_classess = (IsTokenValid, IsValidGroupUser)
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        Overriding queryset method 
        Fetches record according to owner and membership of a group
        """
        contact_info = Contact.objects.prefetch_related(
            Prefetch(
                'group_group_contacts',
                queryset=Group.objects.filter(Q(owner=self.request.user) | Q(
                    group_members_in=[self.request.user, ])),
            )
        )
        return contact_info
