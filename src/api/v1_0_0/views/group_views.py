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
from ..permissions.token_permissions import IsBlackListedToken
from ..permissions.group_permissions import IsValidGroupUser


class GroupViewSet(viewsets.ModelViewSet):
    """
    Viewset for Group
    """
    serializer_class = GroupSerializer
    permission_classess = (IsBlackListedToken, IsValidGroupUser)

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
        group_info = Group.objects.filter(id__in=Member.objects.filter(
            user=self.request.user).values('id').distinct())
        return group_info

    @action(detail=True, methods=['GET'])
    def member(self, request, **kwargs):
        """
        Method to fetch group members using group id
        """
        group_obj = self.get_object()
        member_data = group_obj.members.all()
        print(member_data)
        if member_data is not None:
            serializer_data = MemberSerializer(member_data, many=True)
            return Response(serializer_data.data)
        else:
            return Response({'message': 'No details found'}, status=status.HTTP_404_NOT_FOUND)


class ContactViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining group contact
    """
    permission_classess = (IsBlackListedToken, IsValidGroupUser)
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        Overriding queryset method 
        Fetches record according to owner and membership of a group
        """
        contact_data = Contact.objects.filter(contact_groups__in=Member.objects.filter(
            user=self.request.user).values('id').distinct())

        return contact_data


class MemberViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining group Member
    """
    queryset = Member.objects.all()
    permission_classess = (IsBlackListedToken, IsValidGroupUser)
    serializer_class = MemberSerializer

    def get_serializer_context(self, *args, **kwargs):
        """
        Passing request object to Member serializer
        """
        return {'request': self.request}
