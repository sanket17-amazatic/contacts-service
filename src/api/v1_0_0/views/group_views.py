"""
View for Group and group member detials
"""
from django.db.models import (Q,)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from group.models import (Group, Contact, Member)
from ..serializers.group_serializers import (
    GroupSerializer, ContactSerializer, MemberSerializer)
from ..permissions.token_permissions import IsTokenValid
from ..permissions.group_permissions import IsValidGroupUser

class GroupViewSet(viewsets.ModelViewSet):
    """
    Viewset for Group
    """
    serializer_class = GroupSerializer
    permission_classess = (IsTokenValid, IsValidGroupUser)

    def get_serializer_context(self, *args, **kwargs):
        """
        Passing request data to Group serializer
        """
        return {'request': self.request}

    def get_queryset(self):
        """
        Overriding queryset method 
        Fetches record according to owner and membership of a user
        """
        group_id_list = list(Member.objects.filter(
            user=self.request.user).values_list('group', flat=True))
        group_info = Group.objects.filter(id__in=group_id_list)
        return group_info
    
    @action(detail=True, methods=['GET'])
    def member(self, request, id=None, **kwargs):
        """
        Method to fetch group members using group id
        """
        if id is None:
            return Response({'message':'id not found'}, status=status.HTTP_400_BAD_REQUEST) 
        member_data = Member.objects.filter(group_id=id)
        if member_data is not None:
            return Response(member_data)
        else:
            return Response({'message':'No details found'}, status=status.HTTP_404_NOT_FOUND)


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
        group_id_list = list(Member.objects.filter(
            user=self.request.user).values_list('group', flat=True))
        contact_data = Contact.objects.filter(group__id__in=group_id_list)        
        return contact_data
    
    
class MemberViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining group Member
    """
    queryset = Member.objects.all()
    permission_classess = (IsTokenValid, IsValidGroupUser)
    serializer_class = ContactSerializer

    def get_serializer_context(self, *args, **kwargs):
        """
        Passing request object to Member serializer
        """
        return {'request': self.request}
