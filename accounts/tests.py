"""
API Test cases for App user model
"""
import json
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse
from rest_framework import status
from .models import (AppUser, BlackListedToken)

class AppUserTest(APITestCase):
    def setUp(self):
        app_user = AppUser.objects.create(username='testuser', email="test@mail.com", phone="+919876543210")
        app_user.set_password('testing123')
        app_user.save()
    """
    Test case class for APP USER
    """
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

    def test_user_mobile_verification_success(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-verify')
        req_data = {
            "phone": "+919876543210"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_mobile_verification_fail(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-verify')
        req_data = {
            "phone": "+919876543211"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_login_success(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-login')
        req_data = {
            "username": "testuser",
            "password": "testing123"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)

    def test_user_login_failure(self):
        """
        Test for user creation
        """
        url = api_reverse('api:user-login')
        req_data = {
            "username": "testuser",
            "password": "testing"
        }
        response_data = self.client.post(url, req_data, format='json')
        print(response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_401_UNAUTHORIZED)
    