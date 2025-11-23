"""
Tests for CustomUser model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.rbac.models import Role, Permission

User = get_user_model()


class CustomUserModelTestCase(TestCase):
    """Test CustomUser model"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)
    
    def test_create_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='TestPass123!')
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_create_superuser_without_staff(self):
        """Test creating superuser with is_staff=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='AdminPass123!',
                is_staff=False
            )
    
    def test_get_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_full_name(), 'Test User')
        
        # Test with no name
        user.first_name = ''
        user.last_name = ''
        user.save()
        self.assertEqual(user.get_full_name(), user.email)
    
    def test_get_short_name(self):
        """Test get_short_name method"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_short_name(), 'Test')
        
        # Test with no first name
        user.first_name = ''
        user.save()
        self.assertEqual(user.get_short_name(), 'test')
    
    def test_email_normalization(self):
        """Test email is normalized"""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='TestPass123!'
        )
        
        self.assertEqual(user.email, 'TEST@example.com')  # Domain is lowercase
    
    def test_unique_email(self):
        """Test email uniqueness constraint"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)
    
    def test_str_method(self):
        """Test string representation"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(str(user), user.email)
    
    def test_metadata_field(self):
        """Test metadata JSON field"""
        user = User.objects.create_user(**self.user_data)
        
        # Default empty dict
        self.assertEqual(user.metadata, {})
        
        # Set metadata
        user.metadata = {'preference': 'dark_mode', 'language': 'en'}
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.metadata['preference'], 'dark_mode')
        self.assertEqual(user.metadata['language'], 'en')


class CustomUserRBACTestCase(TestCase):
    """Test CustomUser RBAC methods"""
    
    def setUp(self):
        """Set up test data"""
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
        
        # Create role
        self.role = Role.objects.create(
            name='Test Role',
            slug='test-role',
            level=10
        )
        self.role.permissions.add(self.permission1, self.permission2)
    
    def test_assign_role(self):
        """Test assigning role to user"""
        user_role = self.user.assign_role(self.role)
        
        self.assertIsNotNone(user_role)
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertTrue(user_role.is_active)
    
    def test_assign_role_by_slug(self):
        """Test assigning role by slug"""
        user_role = self.user.assign_role('test-role')
        
        self.assertIsNotNone(user_role)
        self.assertEqual(user_role.role, self.role)
    
    def test_has_role(self):
        """Test checking if user has role"""
        self.assertFalse(self.user.has_role('test-role'))
        
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_role('test-role'))
    
    def test_has_permission(self):
        """Test checking if user has permission"""
        self.assertFalse(self.user.has_permission('user.view'))
        
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_permission('user.view'))
        self.assertTrue(self.user.has_permission('user.create'))
        self.assertFalse(self.user.has_permission('user.delete'))
    
    def test_get_active_roles(self):
        """Test getting user's active roles"""
        self.user.assign_role(self.role)
        
        active_roles = self.user.get_active_roles()
        self.assertEqual(active_roles.count(), 1)
        self.assertEqual(active_roles.first().role, self.role)
    
    def test_get_primary_role(self):
        """Test getting user's primary role"""
        self.user.assign_role(self.role, is_primary=True)
        
        primary_role = self.user.get_primary_role()
        self.assertEqual(primary_role, self.role)
    
    def test_get_all_permissions(self):
        """Test getting all user permissions"""
        self.user.assign_role(self.role)
        
        permissions = self.user.get_all_permissions()
        self.assertEqual(permissions.count(), 2)
        self.assertIn(self.permission1, permissions)
        self.assertIn(self.permission2, permissions)
    
    def test_revoke_role(self):
        """Test revoking role from user"""
        self.user.assign_role(self.role)
        self.assertTrue(self.user.has_role('test-role'))
        
        self.user.revoke_role(self.role)
        self.assertFalse(self.user.has_role('test-role'))
