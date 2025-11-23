"""
API Tests for authentication endpoints
"""
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalSubscript=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportOptionalOperand=false
# pyright: reportArgumentType=false
from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser as User
else:
    User = get_user_model()
    APIClient = APIClient  # For runtime


class AuthenticationAPITestCase(TestCase):
    """Test authentication API endpoints"""
    
    client: APIClient  # Type hint for Pylance
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('rest_register')
        data = {
            'email': 'newuser@example.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        # dj-rest-auth may return different status codes
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_204_NO_CONTENT])
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        url = reverse('rest_register')
        data = {
            'email': 'newuser@example.com',
            'password1': 'NewPass123!',
            'password2': 'DifferentPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_email(self):
        """Test registration with existing email"""
        url = reverse('rest_register')
        data = {
            'email': 'test@example.com',  # Already exists
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse('rest_login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that response has some form of authentication data
        self.assertTrue(len(response.data) > 0, "Response should contain authentication data")
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('rest_login')
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout endpoint"""
        # Login first
        login_url = reverse('rest_login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Authenticate for subsequent requests
        if 'access' in login_response.data:  # type: ignore[operator]
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')  # type: ignore[index]
        elif 'key' in login_response.data:  # type: ignore[operator]
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {login_response.data["key"]}')  # type: ignore[index]
        
        # Logout
        logout_url = reverse('rest_logout')
        logout_data = {}
        if 'refresh' in login_response.data:  # type: ignore[operator]
            logout_data['refresh'] = login_response.data['refresh']  # type: ignore[index]
        
        response = self.client.post(logout_url, logout_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Login first
        login_url = reverse('rest_login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Only test refresh if JWT is being used
        if 'refresh' not in login_response.data:
            self.skipTest("JWT not enabled, skipping token refresh test")
        
        # Refresh token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': login_response.data['refresh']
        }
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_get_user_profile(self):
        """Test getting authenticated user profile"""
        # Login first
        login_url = reverse('rest_login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Authenticate
        if 'access' in login_response.data:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        elif 'key' in login_response.data:
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {login_response.data["key"]}')
        
        # Get user profile
        url = reverse('rest_user_details')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        # Login first
        login_url = reverse('rest_login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Authenticate
        if 'access' in login_response.data:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        elif 'key' in login_response.data:
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {login_response.data["key"]}')
        
        # Update profile
        url = reverse('rest_user_details')
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without authentication"""
        url = reverse('rest_user_details')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
