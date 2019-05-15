"""
View for Group and group member detials
"""
from django.db.models import (Q,)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from group.models import (Group, Contact, Member)
from ..serializers.group_serializers import (
    GroupSerializer, ContactSerializer, MemberSerializer, ContactCreationAndUpdationMixin)
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
            user=self.request.user).values('group').distinct())
        return group_info

    @action(detail=True, methods=['GET'])
    def member(self, request, **kwargs):
        """
        Method to fetch group members using group id
        """
        group_obj = self.get_object()
        member_data = group_obj.members.all()
        if member_data is not None:
            serializer_data = MemberSerializer(member_data, many=True)
            return Response(serializer_data.data)
        else:
            return Response({'message': 'No details found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['GET'])
    def contact(self, request, **kwargs):
        """
        Method to fetch group contact using group id
        """
        group_obj = self.get_object()
        contact_data = group_obj.contacts.all()
        if contact_data is not None:
            serializer_data = ContactSerializer(contact_data, many=True)
            return Response(serializer_data.data)
        else:
            return Response({'message': 'No details found for contact of this group'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], url_path='add-member', url_name='add_member')
    def add_member(self, request, **kwargs):
        """
        Method to add group member using group id
        """
        if request.data.get('phone') is None:
            return Response({'message': 'Phone number not provided'}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('role') is None:
            return Response({'message': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
        req_user = request.data.get('phone')
        user_data = User.objects.get(phone=req_user)
        if user_data is None:
            return Response({'message': 'User with this number is not registered'}, status=status.HTTP_404_NOT_FOUND)
        group = self.get_object()
        if group.members.filter(user=user_data).count() != 0:
            return Response({'message': 'User is already member of this group'}, status=status.HTTP_400_BAD_REQUEST)
        member_role = request.data.get('role')
        new_member_data = Member.objects.create(group=group, user=user_data,role_type=member_role)
        new_member_data.save()
        serializer_data = MemberSerializer(new_member_data)
        return Response(serializer_data.data)

    @action(detail=True, methods=['POST'], url_path='add-contact', url_name='add_contact')
    def add_contact(self, request, **kwargs):
        """
        Method to add contact to group using id
        """
        if request.data is None:
            return Response({'message': 'Invalid contact details'}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('first_name') is None:
            return Response({'message': 'First name not provided'}, status=status.HTTP_400_BAD_REQUEST)
        new_contact_data = ContactCreationAndUpdationMixin().create(request.data)
        group = self.get_object()
        group.contacts.add(new_contact_data)
        serializer_data = ContactSerializer(new_contact_data)       
        return Response(serializer_data.data)

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
