'''
View for Group and group member detials
'''
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import (Group, Member)
from .api.serializer import (GroupSerializer, MemberSerializer)
from accounts.api.permissions import IsTokenValid

class GroupViewSet(viewsets.ModelViewSet):
    '''
    Viewset for Group
    '''
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classess = [IsTokenValid]
    authentication_classess = []

class MemberViewSet(viewsets.ModelViewSet):
    '''
    Viewset for maintaining group member
    '''
    queryset = Member.objects.all()
    permission_classess = [IsTokenValid]
    serializer_class = MemberSerializer
