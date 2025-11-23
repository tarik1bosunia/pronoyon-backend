"""
API Tests for RBAC endpoints
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.rbac.models import Permission, Role, UserRole

User = get_user_model()


class PermissionAPITestCase(TestCase):
    """Test Permission API endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Create permissions
        self.permission1 = Permission.objects.create(
            name='user.view',
            codename='user-view',
            description='View users',
            category='user'
        )
        self.permission2 = Permission.objects.create(
            name='user.create',
            codename='user-create',
            description='Create users',
            category='user'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_list_permissions(self):
        """Test listing all permissions"""
        url = reverse('permission-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_permission(self):
        """Test retrieving a single permission"""
        url = reverse('permission-detail', args=[self.permission1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'user.view')
        self.assertEqual(response.data['category'], 'user')
    
    def test_filter_permissions_by_category(self):
        """Test filtering permissions by category"""
        # Create permission in different category
        Permission.objects.create(
            name='content.view',
            codename='content-view',
            category='content'
        )
        
        url = reverse('permission-list')
        response = self.client.get(url, {'category': 'user'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_permissions(self):
        """Test searching permissions"""
        url = reverse('permission-list')
        response = self.client.get(url, {'search': 'view'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class RoleAPITestCase(TestCase):
    """Test Role API endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!',
            is_staff=True
        )
        
        # Create permissions
        self.permission1 = Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
        self.permission2 = Permission.objects.create(
            name='user.create',
            codename='user-create',
            category='user'
        )
        
        # Create role
        self.role = Role.objects.create(
            name='Manager',
            slug='manager',
            description='Manager role',
            level=60
        )
        self.role.permissions.add(self.permission1, self.permission2)
        
        # Authenticate
        self.client.force_authenticate(user=self.admin)
    
    def test_list_roles(self):
        """Test listing all roles"""
        url = reverse('role-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_retrieve_role(self):
        """Test retrieving a single role"""
        url = reverse('role-detail', args=[self.role.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Manager')
        self.assertEqual(response.data['slug'], 'manager')
        self.assertEqual(response.data['level'], 60)
    
    def test_create_role(self):
        """Test creating a new role"""
        url = reverse('role-list')
        data = {
            'name': 'Editor',
            'slug': 'editor',
            'description': 'Content editor role',
            'level': 30,
            'role_type': 'custom',
            'permissions': [self.permission1.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Editor')
        self.assertEqual(response.data['slug'], 'editor')
    
    def test_update_role(self):
        """Test updating a role"""
        url = reverse('role-detail', args=[self.role.id])
        data = {
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')
    
    def test_delete_role(self):
        """Test deleting a role"""
        url = reverse('role-detail', args=[self.role.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(id=self.role.id).exists())
    
    def test_filter_roles_by_level(self):
        """Test filtering roles by level"""
        # Create another role
        Role.objects.create(
            name='Admin',
            slug='admin',
            level=70
        )
        
        url = reverse('role-list')
        response = self.client.get(url, {'level': 60})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserRoleAPITestCase(TestCase):
    """Test UserRole API endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!',
            is_staff=True
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='UserPass123!'
        )
        
        # Create permissions
        permission = Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
        
        # Create role
        self.role = Role.objects.create(
            name='User',
            slug='user',
            level=10
        )
        self.role.permissions.add(permission)
        
        # Authenticate
        self.client.force_authenticate(user=self.admin)
    
    def test_list_user_roles(self):
        """Test listing all user role assignments"""
        # Assign role
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )
        
        url = reverse('userrole-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_assign_role_to_user(self):
        """Test assigning role to user"""
        url = reverse('userrole-list')
        data = {
            'user': self.user.id,
            'role': self.role.id,
            'is_primary': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_primary'])
        self.assertTrue(response.data['is_active'])
    
    def test_revoke_role_from_user(self):
        """Test revoking role from user"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )
        
        url = reverse('userrole-detail', args=[user_role.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_update_user_role(self):
        """Test updating user role assignment"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )
        
        url = reverse('userrole-detail', args=[user_role.id])
        data = {
            'notes': 'Updated notes'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'Updated notes')
    
    def test_filter_user_roles_by_user(self):
        """Test filtering user roles by user"""
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )
        
        url = reverse('userrole-list')
        response = self.client.get(url, {'user': self.user.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_filter_active_user_roles(self):
        """Test filtering active user roles"""
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True
        )
        UserRole.objects.create(
            user=User.objects.create_user(email='user2@example.com', password='pass'),
            role=self.role,
            is_active=False
        )
        
        url = reverse('userrole-list')
        response = self.client.get(url, {'is_active': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CurrentUserRBACAPITestCase(TestCase):
    """Test current user RBAC endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Create permissions
        self.permission1 = Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
        self.permission2 = Permission.objects.create(
            name='user.create',
            codename='user-create',
            category='user'
        )
        
        # Create role and assign to user
        self.role = Role.objects.create(
            name='User',
            slug='user',
            level=10
        )
        self.role.permissions.add(self.permission1, self.permission2)
        
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_primary=True
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_get_current_user_roles(self):
        """Test getting current user's roles"""
        url = reverse('current-user-rbac-my-roles')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['role']['name'], 'User')
    
    def test_get_current_user_permissions(self):
        """Test getting current user's permissions"""
        url = reverse('current-user-rbac-my-permissions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_check_user_permission(self):
        """Test checking if current user has permission"""
        url = reverse('current-user-rbac-has-permission')
        data = {'permission': 'user.view'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_permission'])
        
        # Test permission user doesn't have
        data = {'permission': 'user.delete'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_permission'])
    
    def test_unauthorized_access(self):
        """Test accessing RBAC endpoints without authentication"""
        self.client.force_authenticate(user=None)
        
        url = reverse('current-user-rbac-my-roles')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
