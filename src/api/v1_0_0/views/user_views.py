"""
View for contact user application user
"""
import requests
import phonenumbers
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
from utils.jwt_utils import (jwt_response_payload_handler, jwt_payload_handler)
from utils.otp_utils import TOTPVerification
from utils.send_sms_utils import Message
from ..serializers.user_serializers import (
    UserSerializer, BlackListedTokenSerializer)
from ..permissions.token_permissions import IsBlackListedToken
from ..permissions.user_permissions import IsListAction

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for User
    """
    otp = TOTPVerification()
    serializer_class = UserSerializer
    public_action_list = ['forget', 'login', 'verify', 'create', 'get_otp', 'verify_otp', 'set_password']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in self.public_action_list:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsBlackListedToken,
                                  permissions.IsAuthenticated, IsListAction]
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

    @action(detail=False, methods=['POST'], url_path='set-password', url_name='set_password')
    def set_password(self, request, **kwargs):
        """
        Action function executed for reseting forgotten password
        """

        try:
            user_obj =  User.objects.get(phone=request.data.get('phone'))
        except User.DoesNotExist:
            return Response({'details': 'User with this number is not registered'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        entered_password = request.data.get('password')
        confirmed_password = request.data.get('password2')
        if entered_password != confirmed_password:
            return Response({'details': 'Entered password didnot match'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user_obj.set_password(entered_password)
        user_obj.save()
        serializer_data = UserSerializer(user_obj)
        return Response(serializer_data.data)

    @action(detail=False, methods=['POST'], url_path='verify-otp', url_name='verify_otp')
    def verify_otp(self, request, **kwargs):
        """
        This method is used to verify the otp
        """
        req_otp = request.data.get('otp')
        valid_flag = self.otp.verify_token(req_otp)
        return Response({'valid': valid_flag})

    @action(detail=False, methods=['POST'], url_path='otp', url_name='get_otp')
    def get_otp(self, request, **kwargs):
        """
        This method verifies the number and then send otp
        """
        valid_user = User.objects.filter(
            phone=request.data.get('phone')).exists()
        if request.data.get('action') == 'Forget Password' and not valid_user:
            return Response({'details': 'Phone number not registered'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif request.data.get('action') == 'Signup' and valid_user:
            return Response({'details': 'User already registered'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            parse_number = phonenumbers.parse(request.data.get('phone'), None)
        except Exception:
            return Response({'details': 'Invalid Phonenumber'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if phonenumbers.is_valid_number(parse_number):
            number = request.data.get('phone')
        else:
            return Response({'details': 'Invalid Phonenumber entered'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        token = self.otp.generate_token()
        otp_message = f"Dear Customer, your OTP is {token} which is valid for 5 minutes"
        # otp_message = otp_message.replace(' ','%20') 

        send_values = {
            'mobiles': number[1:],
            'message': otp_message
        }

        send_sms = Message('68904AqY6Ddphfu5cf5b375')
        response = send_sms.send(send_values)

        # conn_url = "https://control.msg91.com/api/sendhttp.php"
       
        #sms_service_url = f'/api/sendhttp.php?authkey=68904AqY6Ddphfu5cf5b375&mobiles={number[1:]}&message={otp_message}&sender=1SHIPCO&route=4&country=0'
        # querystring = {
        #     "authkey":"68904AqY6Ddphfu5cf5b375",
        #     "mobiles":number[1:],
        #     "message":otp_message,
        #     "sender":"1SHARE",
        #     "route":"4",
        #     "country":"0"
        #     }

        # payload = ""
        # headers = {
        #     'cache-control': "no-cache"
        # }

        # response = requests.request("POST", conn_url, data=payload, headers=headers, params=querystring)
        if response.status_code == 200:
            return Response({'details':'SMS sent to entered mobile number'}, status=status.HTTP_200_OK)
        else:
            return Response({'details': 'Failed to sent sms', 'error':response.text, 'status_code': response.status_code}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def verify(self, request, **kwargs):
        """
        Method to check phone number is registered or not
        """
        req_phone = request.data.get('phone', None)
        if req_phone is None:
            return Response({'details': 'Phone number cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone=req_phone)
        if user.count() > 0:
            return Response({'register': 'True'}, status=status.HTTP_200_OK)
        else:
            return Response({'register': 'False'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def login(self, request, **kwargs):
        """
        Action method for app user login
        """
        if request.user.is_authenticated:
            return Response({'details': 'You are already authenticated'})

        req_phone = request.data.get('phone')
        req_password = request.data.get('password')
        if req_phone is None or req_password is None:
            return Response({'details': 'User phone number or password is empty'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(phone=req_phone, password=req_password)
        if user is not None:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            response_data = jwt_response_payload_handler(token, user, request)
            return Response(response_data)
        return Response({'details': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutViewSet(viewsets.ModelViewSet):
    """
    Viewset for maintaining blacklisted token
    """
    queryset = BlackListedToken.objects.all()
    serializer_class = BlackListedTokenSerializer

    def get_serializer_context(self, *args, **kwargs):
        """
        Passing request data to User serializer
        """
        return {'request': self.request}
