"""
API Test cases for App user model
"""
import json
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import (User, BlackListedToken)

class UserTest(APITestCase):
    """
    Test case class for USER
    """
    auth_token = ''

    def setUp(self):
        """
        Setup method for creating a user for all test
        """
        app_user = User.objects.create(username='testuser', email="test@mail.com", phone="+919876543210")
        app_user.set_password('testing123')
        app_user.save()

    def set_token(self, username='testuser', password='testing123', set_flag=True):
        url = api_reverse('api:user-login')
        req_data = {
            "username": 'testuser',
            "password": 'testing123'
        }
        response_data = self.client.post(url, req_data, format='json')
        self.auth_token = response_data.data['token']
        self.client = APIClient()
        if set_flag is True:    
            self.client.credentials(HTTP_AUTHORIZATION='JWT ' + response_data.data['token'])
        else:
            self.client.credentials()
        return self.client

    def test_user_registration_wrong_password(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-list')
        req_data = {
            "username": "sam",
            "password": "sam@123",
            "password2": "sam@123345",
            "email": "john@gmail.com",
            "phone": "+918976543220"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_for_existing_user(self):
        """
        Test for user registration which is already created
        """
        url = api_reverse('api:user-list')
        req_data = {
            "username": "john",
            "password": "admin@123",
            "password2": "admin@123345",
            "email": "john@gmail.com",
            "phone": "+918976543210"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        """
        Test for user logout
        """
        url = api_reverse('api:logout-list')
        self.client = self.set_token()
        req_data = {
            'user' : 1,
            'token' : self.auth_token
        }
        response_data = self.client.post(url, req_data, format='json')
        print('Logout data:',response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_registration_success(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-list')
        req_data = {
            "username": "john",
            "password": "admin@123",
            "password2": "admin@123",
            "email": "john@gmail.com",
            "phone": "+918976543210"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_201_CREATED)

    def test_user_fetch_list(self):
        """
        Test to fetch list of all user
        """
        url = api_reverse('api:user-list')
        self.client = self.set_token()
        response_data = self.client.get(url, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_mobile_verification_success(self):
        """
        Test to check for user mobile registrations
        """
        url = api_reverse('api:user-verify')
        req_data = {
            "phone": "+919876543210"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_mobile_verification_fail(self):
        """
        Test to check user un registered mobile
        """
        url = api_reverse('api:user-verify')
        req_data = {
            "phone": "+919876543211"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_nomobile_verification(self):
        """
        Test to check when user provides no mobile number
        """
        url = api_reverse('api:user-verify')
        req_data = {
            "phone": None
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """
        Test to check user login success
        """
        url = api_reverse('api:user-login')
        req_data = {
            "username": "testuser",
            "password": "testing123"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_login_no_password(self):
        """
        Test to check login when user provides no password
        """
        url = api_reverse('api:user-login')
        req_data = {
            "username": "testuser"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_no_username(self):
        """
        Test to check login when user provides no username
        """
        url = api_reverse('api:user-login')
        req_data = {
            "password": "testing"
        }
        response_data = self.client.post(url, req_data, format='json')
        self.assertEqual(response_data.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_failure(self):
        """
        Test to check login when wrong credentials provided
        """
        url = api_reverse('api:user-login')
        req_data = {
            "username": "testuser",
            "password": "testing"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_401_UNAUTHORIZED)
    