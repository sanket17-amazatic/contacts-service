'''
Utility for generating payload for jwt token
'''
import datetime
from django.utils import timezone
from django.conf import settings

expiry_delta = settings.JWT_AUTH['JWT_REFRESH_EXPIRATION_DELTA']


def jwt_response_payload_handler(token, user=None, request=None):
    '''
    Function returns jwt payload response on login 
    '''
    return {
        'token': token,
        'user': user.username,
        'expire': timezone.now() + expiry_delta - datetime.timedelta(seconds=200)
    }