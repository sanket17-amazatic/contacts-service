"""
View for contact user application user
"""
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings
from .models import (AppUser, BlackListedToken)
from .api.serializer import (AppUserSerializer, BlackListedTokenSerializer)
from .api.utils import jwt_response_payload_handler
from .api.permissions import IsTokenValid

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class AppUserViewSet(viewsets.ModelViewSet):
    """
    Viewset for AppUser
    """
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    action_list = ['forget', 'login', 'verify', 'create']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in self.action_list:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsTokenValid, permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['POST'])
    def forget(self, request, **kwargs):
        """
        Action function executed for reseting forgotten password
        """
        user_obj = self.get_object()
        entered_phone = kwargs['phone']
        if entered_phone != user_obj.phone:
            return Response({'details':'Entered phone number does not match with registered phone number'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        entered_password = kwargs['password']
        confirmed_password = kwargs['password2']
        if entered_password != confirmed_password:
            return Response({'details':'Entered password didnot match'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user_obj.set_password(entered_password)
        user_obj.save()
        serializer_data = AppUserSerializer(user_obj)
        return Response(serializer_data.data)
    
    @action(detail=False, methods=['POST'])
    def send_otp(self, request, **kwargs):
        pass

    @action(detail=False, methods=['POST'])
    def verify_otp(self, request, **kwargs):
        pass

    @action(detail=False, methods=['POST'])
    def verify(self, request, **kwargs):
        """
        Method to check phone number is registered or not
        """
        req_phone = request.data.get('phone', None)
        if req_phone is None:
            return Response({'details':'Phone number cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = AppUser.objects.filter(phone=req_phone)
        if user.count() > 0:
            return Response({'register':'True'}, status=status.HTTP_200_OK)
        else:
            return Response({'register':'False'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def login(self, request, **kwargs):
        """
        Action method for app user login
        """
        if request.user.is_authenticated:
            return Response({'details':'You are already authenticated'})

        req_username = request.data.get('username')
        req_password = request.data.get('password')
        if req_username is None or req_password is None:
            return Response({'details':'Username or password is empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=req_username, password=req_password)
        if user is not None:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            response_data = jwt_response_payload_handler(token, user, request)
            return Response(response_data)
        return Response({'details':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining blacklisted token
    """
    queryset = BlackListedToken.objects.all()
    serializer_class = BlackListedTokenSerializer
