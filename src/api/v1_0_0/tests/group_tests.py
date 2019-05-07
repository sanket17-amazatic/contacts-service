"""
API Test cases for Groups and groups contactsS
"""
import json
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse
from rest_framework import status
from rest_framework.test import APIClient
from account.models import (AppUser, BlackListedToken)
from groups.models import (Groups, Contact, ContactNumber)

class GroupTest(APITestCase):
    """
    Test case for groups
    """
    def setUp(self):
        """
        Setup method for creating a user for all test
        """
        app_user = AppUser.objects.create(username='testuser', email="test@mail.com", phone="+919876543210")
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
    
    def test_create_group(self):
        """
        Test for creating group logout
        """
        url = api_reverse('api:group-list')
        self.client = self.set_token()
        req_data = {
            'user' : 1,
            'token' : self.auth_token
        }
        response_data = self.client.post(url, req_data, format='json')
        print('Logout data:',response_data.data)
        self.assertEqual(response_data.status_code, status.HTTP_200_OK)
        