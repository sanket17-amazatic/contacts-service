"""
View for contact user application user
"""
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework_jwt.settings import api_settings
from user.models import (User, BlackListedToken)
from utils.jwt_utils import (jwt_response_payload_handler,jwt_payload_handler)
from utils.otp_utils import TOTPVerification
from ..serializers.user_serializers import (UserSerializer, BlackListedTokenSerializer)
from ..permissions.token_permissions import IsBlackListedToken
from ..permissions.user_permissions import IsListAction

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for User
    """
    otp = TOTPVerification()
    serializer_class = UserSerializer
    public_action_list = ['forget', 'login', 'verify', 'create']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in self.public_action_list:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsBlackListedToken, permissions.IsAuthenticated, IsListAction]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Overriding queryset method 
        Fetches record according of the requested user
        """
        return User.objects.filter(phone=self.request.user.phone)
    
    def get_serializer_context(self, *args, **kwargs):
        """
        Passing request data to User serializer
        """
        return {'request': self.request}

    @action(detail=False, methods=['POST'])
    def set_password(self, request, **kwargs):
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
        serializer_data = UserSerializer(user_obj)
        return Response(serializer_data.data)
    
    @action(detail=False, methods=['POST'])
    def verify_otp(self, request, **kwargs):
        req_otp = request.data.get('otp')
        req_otp = int(req_otp)
        valid_flag = self.otp.verify_token(req_otp)
        return Response({'valid':valid_flag}) 

    @action(detail=False, methods=['GET'])
    def get_otp(self, request, **kwargs):
        token = self.otp.generate_token()
        return Response({'otp': token})

    @action(detail=False, methods=['POST'])
    def verify(self, request, **kwargs):
        """
        Method to check phone number is registered or not
        """
        req_phone = request.data.get('phone', None)
        if req_phone is None:
            return Response({'details':'Phone number cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone=req_phone)
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

        req_phone = request.data.get('phone')
        req_password = request.data.get('password')
        if req_phone is None or req_password is None:
            return Response({'details':'User phone number or password is empty'}, status=status.HTTP_400_BAD_REQUEST) 
        user = authenticate(phone=req_phone, password=req_password)
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
