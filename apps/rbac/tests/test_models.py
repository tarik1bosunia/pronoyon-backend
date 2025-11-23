"""
Tests for RBAC models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.rbac.models import Permission, Role, UserRole, RoleHistory

User = get_user_model()


class PermissionModelTestCase(TestCase):
    """Test Permission model"""
    
    def test_create_permission(self):
        """Test creating a permission"""
        permission = Permission.objects.create(
            name='user.view',
            codename='user-view',
            description='View user details',
            category='user'
        )
        
        self.assertEqual(permission.name, 'user.view')
        self.assertEqual(permission.codename, 'user-view')
        self.assertEqual(permission.category, 'user')
        self.assertTrue(permission.is_active)
    
    def test_permission_name_format_validation(self):
        """Test permission name must be in format resource.action"""
        with self.assertRaises(ValidationError):
            permission = Permission(
                name='invalid_format',  # Missing dot
                codename='invalid-format',
                category='user'
            )
            permission.save()
    
    def test_permission_str_method(self):
        """Test permission string representation"""
        permission = Permission.objects.create(
            name='user.create',
            codename='user-create',
            category='user'
        )
        
        self.assertEqual(str(permission), 'user.create (user)')
    
    def test_permission_uniqueness(self):
        """Test permission name and codename uniqueness"""
        Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
        
        # Duplicate name
        with self.assertRaises(Exception):
            Permission.objects.create(
                name='user.view',
                codename='user-view-2',
                category='user'
            )
        
        # Duplicate codename
        with self.assertRaises(Exception):
            Permission.objects.create(
                name='user.view2',
                codename='user-view',
                category='user'
            )


class RoleModelTestCase(TestCase):
    """Test Role model"""
    
    def setUp(self):
        """Set up test data"""
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
        self.permission3 = Permission.objects.create(
            name='user.delete',
            codename='user-delete',
            category='user'
        )
    
    def test_create_role(self):
        """Test creating a role"""
        role = Role.objects.create(
            name='Admin',
            slug='admin',
            description='Administrator role',
            level=70,
            role_type='system'
        )
        
        self.assertEqual(role.name, 'Admin')
        self.assertEqual(role.slug, 'admin')
        self.assertEqual(role.level, 70)
        self.assertTrue(role.is_active)
        self.assertFalse(role.is_default)
    
    def test_role_permissions(self):
        """Test assigning permissions to role"""
        role = Role.objects.create(
            name='Manager',
            slug='manager',
            level=60
        )
        
        role.permissions.add(self.permission1, self.permission2)
        
        self.assertEqual(role.permissions.count(), 2)
        self.assertIn(self.permission1, role.permissions.all())
        self.assertIn(self.permission2, role.permissions.all())
    
    def test_role_inheritance(self):
        """Test role can inherit from parent role"""
        parent_role = Role.objects.create(
            name='Base Role',
            slug='base-role',
            level=10
        )
        parent_role.permissions.add(self.permission1)
        
        child_role = Role.objects.create(
            name='Child Role',
            slug='child-role',
            level=20,
            inherits_from=parent_role
        )
        child_role.permissions.add(self.permission2)
        
        # Child should have both its own and inherited permissions
        all_permissions = child_role.get_all_permissions()
        self.assertEqual(all_permissions.count(), 2)
        self.assertIn(self.permission1, all_permissions)
        self.assertIn(self.permission2, all_permissions)
    
    def test_role_has_permission(self):
        """Test checking if role has permission"""
        role = Role.objects.create(
            name='Editor',
            slug='editor',
            level=30
        )
        role.permissions.add(self.permission1, self.permission2)
        
        self.assertTrue(role.has_permission('user.view'))
        self.assertTrue(role.has_permission('user.create'))
        self.assertFalse(role.has_permission('user.delete'))
    
    def test_circular_inheritance_prevented(self):
        """Test circular role inheritance is prevented"""
        role1 = Role.objects.create(
            name='Role 1',
            slug='role-1',
            level=10
        )
        
        role2 = Role.objects.create(
            name='Role 2',
            slug='role-2',
            level=20,
            inherits_from=role1
        )
        
        # Try to make role1 inherit from role2 (circular)
        role1.inherits_from = role2
        
        with self.assertRaises(ValidationError):
            role1.save()
    
    def test_role_max_users(self):
        """Test role max users limit"""
        role = Role.objects.create(
            name='Limited Role',
            slug='limited-role',
            level=10,
            max_users=2
        )
        
        self.assertTrue(role.can_assign_more_users())
        
        # Create users and assign role
        user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        user2 = User.objects.create_user(email='user2@example.com', password='pass123')
        
        UserRole.objects.create(user=user1, role=role)
        UserRole.objects.create(user=user2, role=role)
        
        self.assertFalse(role.can_assign_more_users())
        self.assertEqual(role.get_user_count(), 2)
    
    def test_role_str_method(self):
        """Test role string representation"""
        role = Role.objects.create(
            name='Test Role',
            slug='test-role',
            level=50
        )
        
        self.assertEqual(str(role), 'Test Role (Level 50)')


class UserRoleModelTestCase(TestCase):
    """Test UserRole model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        self.role = Role.objects.create(
            name='Test Role',
            slug='test-role',
            level=10
        )
    
    def test_assign_role_to_user(self):
        """Test assigning role to user"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.admin
        )
        
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertEqual(user_role.assigned_by, self.admin)
        self.assertTrue(user_role.is_active)
        self.assertFalse(user_role.is_primary)
    
    def test_primary_role_assignment(self):
        """Test primary role assignment"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_primary=True
        )
        
        self.assertTrue(user_role.is_primary)
        
        # Create another role
        another_role = Role.objects.create(
            name='Another Role',
            slug='another-role',
            level=20
        )
        
        # Try to assign another primary role (should fail)
        with self.assertRaises(ValidationError):
            UserRole.objects.create(
                user=self.user,
                role=another_role,
                is_primary=True
            )
    
    def test_role_expiration(self):
        """Test role expiration"""
        # Create expired role
        expired_time = timezone.now() - timedelta(days=1)
        expired_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            expires_at=expired_time
        )
        
        self.assertTrue(expired_role.is_expired())
        
        # Create non-expired role
        future_time = timezone.now() + timedelta(days=30)
        active_role = UserRole.objects.create(
            user=User.objects.create_user(email='user2@example.com', password='pass'),
            role=self.role,
            expires_at=future_time
        )
        
        self.assertFalse(active_role.is_expired())
        
        # Create role without expiration
        permanent_role = UserRole.objects.create(
            user=User.objects.create_user(email='user3@example.com', password='pass'),
            role=self.role
        )
        
        self.assertFalse(permanent_role.is_expired())
    
    def test_role_context(self):
        """Test role context field"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            context={'workspace_id': 123, 'project_id': 456}
        )
        
        self.assertEqual(user_role.context['workspace_id'], 123)
        self.assertEqual(user_role.context['project_id'], 456)
    
    def test_max_users_limit_enforced(self):
        """Test max users limit is enforced"""
        limited_role = Role.objects.create(
            name='Limited Role',
            slug='limited-role',
            level=10,
            max_users=1
        )
        
        # First assignment should succeed
        UserRole.objects.create(user=self.user, role=limited_role)
        
        # Second assignment should fail
        user2 = User.objects.create_user(email='user2@example.com', password='pass')
        
        with self.assertRaises(ValidationError):
            UserRole.objects.create(user=user2, role=limited_role)
    
    def test_user_role_str_method(self):
        """Test UserRole string representation"""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        
        self.assertEqual(str(user_role), f'{self.user.email} - {self.role.name}')


class RoleHistoryModelTestCase(TestCase):
    """Test RoleHistory model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        self.role = Role.objects.create(
            name='Test Role',
            slug='test-role',
            level=10
        )
    
    def test_create_role_history(self):
        """Test creating role history entry"""
        history = RoleHistory.objects.create(
            user=self.user,
            role=self.role,
            action='assigned',
            performed_by=self.admin,
            reason='User promoted',
            metadata={'notes': 'Excellent performance'}
        )
        
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.role, self.role)
        self.assertEqual(history.action, 'assigned')
        self.assertEqual(history.performed_by, self.admin)
        self.assertEqual(history.reason, 'User promoted')
        self.assertEqual(history.metadata['notes'], 'Excellent performance')
    
    def test_role_history_str_method(self):
        """Test RoleHistory string representation"""
        history = RoleHistory.objects.create(
            user=self.user,
            role=self.role,
            action='revoked',
            performed_by=self.admin
        )
        
        expected = f'{self.user.email} - revoked - {self.role.name}'
        self.assertEqual(str(history), expected)
