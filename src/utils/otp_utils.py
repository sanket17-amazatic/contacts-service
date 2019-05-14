"""
Utility for generating otp
otp is created using TOPT ALGO
"""
import time
from django_otp.oath import TOTP
from django_otp.util import random_hex


class TOTPVerification:
    """
    Class for generating and verifiying the token
    """
    def __init__(self):
        """
        Generating random key, verified counter,
        otp digit and validity period
        """
        self.key = random_hex(20)
        self.last_verified_counter = -1
        self.verified = False
        self.number_of_digits = 6
        self.token_validity_period = 300

    def totp_obj(self):
        """
        create a TOTP object
        """
        totp = TOTP(key=self.key,
                    step=self.token_validity_period,
                    digits=self.number_of_digits)
        totp.time = time.time()
        return totp

    def generate_token(self):
        """
        get the TOTP object and use that to create token
        """
        totp = self.totp_obj()
        token = str(totp.token()).zfill(6)
        return token

    def verify_token(self, token, tolerance=0):
        """
        Verify the passed token
        """
        try:
            token = int(token)
        except ValueError:
            self.verified = False
        else:
            totp = self.totp_obj()
            if ((totp.t() > self.last_verified_counter) and
                    (totp.verify(token, tolerance=tolerance))):
                self.last_verified_counter = totp.t()
                self.verified = True
            else:
                self.verified = False
        return self.verified
