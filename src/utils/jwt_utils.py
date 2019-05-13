"""
Utility for generating payload for jwt token
"""
import jwt
from datetime import (datetime, timedelta)
from calendar import timegm
from django.utils import timezone
from django.conf import settings

expiry_delta = settings.JWT_AUTH['JWT_REFRESH_EXPIRATION_DELTA']

def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    return {
        'user_id': user.pk,
        'user':  str(user.phone),
        'exp': datetime.utcnow() + settings.JWT_AUTH['JWT_EXPIRATION_DELTA'],
        'orig_iat': timegm(
            datetime.utcnow().utctimetuple()
        )
    }

def jwt_response_payload_handler(token, user=None, request=None):
    """
    Function returns jwt payload response on login 
    """
    return {
        'token': token,
        'user':str(user.phone),
        'expire': timezone.now() + expiry_delta - timedelta(seconds=200)
    }
