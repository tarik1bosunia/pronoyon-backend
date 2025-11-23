"""
Tests for RBAC services
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.rbac.models import Permission, Role, UserRole, RoleHistory
from apps.rbac.services import (
    PermissionCheckService,
    UserRoleService,
    RoleService
)

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser as User
else:
    User = get_user_model()


class PermissionCheckServiceTestCase(TestCase):
    """Test PermissionCheckService"""
    
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
        self.permission3 = Permission.objects.create(
            name='user.delete',
            codename='user-delete',
            category='user'
        )
        
        # Create role
        self.role = Role.objects.create(
            name='User',
            slug='user',
            level=10
        )
        self.role.permissions.add(self.permission1, self.permission2)
    
    def test_user_has_permission(self):
        """Test checking if user has permission"""
        # User doesn't have permission yet
        self.assertFalse(
            PermissionCheckService.user_has_permission(self.user, 'user.view')
        )
        
        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)
        
        # Now user should have permission
        self.assertTrue(
            PermissionCheckService.user_has_permission(self.user, 'user.view')
        )
        self.assertTrue(
            PermissionCheckService.user_has_permission(self.user, 'user.create')
        )
        self.assertFalse(
            PermissionCheckService.user_has_permission(self.user, 'user.delete')
        )
    
    def test_user_has_any_permission(self):
        """Test checking if user has any of the permissions"""
        UserRole.objects.create(user=self.user, role=self.role)
        
        # User has at least one permission
        self.assertTrue(
            PermissionCheckService.user_has_any_permission(
                self.user,
                ['user.view', 'user.delete']
            )
        )
        
        # User doesn't have any of these permissions
        self.assertFalse(
            PermissionCheckService.user_has_any_permission(
                self.user,
                ['user.delete', 'admin.access']
            )
        )
    
    def test_user_has_all_permissions(self):
        """Test checking if user has all permissions"""
        UserRole.objects.create(user=self.user, role=self.role)
        
        # User has all these permissions
        self.assertTrue(
            PermissionCheckService.user_has_all_permissions(
                self.user,
                ['user.view', 'user.create']
            )
        )
        
        # User doesn't have all these permissions
        self.assertFalse(
            PermissionCheckService.user_has_all_permissions(
                self.user,
                ['user.view', 'user.delete']
            )
        )
    
    def test_user_has_role(self):
        """Test checking if user has role"""
        self.assertFalse(
            PermissionCheckService.user_has_role(self.user, 'user')
        )
        
        UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertTrue(
            PermissionCheckService.user_has_role(self.user, 'user')
        )
    
    def test_get_user_role_level(self):
        """Test getting user's role level"""
        # User without role should return 0
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.user),
            0
        )
        
        # Assign role
        UserRole.objects.create(user=self.user, role=self.role)
        
        # Should return role level
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.user),
            10
        )
    
    def test_expired_role_permissions(self):
        """Test that expired roles don't grant permissions"""
        # Create expired role assignment
        expired_time = timezone.now() - timedelta(days=1)
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            expires_at=expired_time
        )
        
        # Expired role should not grant permissions
        self.assertFalse(
            PermissionCheckService.user_has_permission(self.user, 'user.view')
        )
    
    def test_inactive_role_permissions(self):
        """Test that inactive roles don't grant permissions"""
        # Create inactive role assignment
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=False
        )
        
        # Inactive role should not grant permissions
        self.assertFalse(
            PermissionCheckService.user_has_permission(self.user, 'user.view')
        )


class UserRoleServiceTestCase(TestCase):
    """Test UserRoleService"""
    
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
            name='User',
            slug='user',
            level=10
        )
    
    def test_assign_role_to_user(self):
        """Test assigning role to user"""
        user_role = UserRoleService.assign_role_to_user(
            user=self.user,
            role=self.role,
            assigned_by=self.admin,
            is_primary=True
        )
        
        self.assertIsNotNone(user_role)
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertEqual(user_role.assigned_by, self.admin)
        self.assertTrue(user_role.is_primary)
        self.assertTrue(user_role.is_active)
        
        # Check role history was created
        self.assertTrue(
            RoleHistory.objects.filter(
                user=self.user,
                role=self.role,
                action='assigned'
            ).exists()
        )
    
    def test_assign_role_with_expiration(self):
        """Test assigning role with expiration"""
        future_time = timezone.now() + timedelta(days=30)
        user_role = UserRoleService.assign_role_to_user(
            user=self.user,
            role=self.role,
            expires_at=future_time
        )
        
        self.assertEqual(user_role.expires_at, future_time)
        self.assertFalse(user_role.is_expired())
    
    def test_assign_role_with_context(self):
        """Test assigning role with context"""
        context = {'workspace_id': 123}
        user_role = UserRoleService.assign_role_to_user(
            user=self.user,
            role=self.role,
            context=context
        )
        
        self.assertEqual(user_role.context, context)
    
    def test_revoke_role_from_user(self):
        """Test revoking role from user"""
        # Assign role first
        UserRoleService.assign_role_to_user(
            user=self.user,
            role=self.role
        )
        
        # Revoke role
        result = UserRoleService.revoke_role_from_user(
            user=self.user,
            role=self.role
        )
        
        # Check role was revoked
        self.assertTrue(result)
        self.assertFalse(
            UserRole.objects.filter(
                user=self.user,
                role=self.role,
                is_active=True
            ).exists()
        )
    
    def test_update_primary_role(self):
        """Test updating primary role"""
        # Create two roles
        role1 = self.role
        role2 = Role.objects.create(
            name='Premium User',
            slug='premium-user',
            level=20
        )
        
        # Assign both roles
        user_role1 = UserRoleService.assign_role_to_user(
            user=self.user,
            role=role1,
            is_primary=True
        )
        user_role2 = UserRoleService.assign_role_to_user(
            user=self.user,
            role=role2
        )
        
        # Make role2 primary
        UserRoleService.set_primary_role(user_role2)
        
        # Refresh from DB
        user_role1.refresh_from_db()
        user_role2.refresh_from_db()
        
        # Check primary status
        self.assertFalse(user_role1.is_primary)
        self.assertTrue(user_role2.is_primary)


class RoleServiceTestCase(TestCase):
    """Test RoleService"""
    
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
    
    def test_create_role_with_permissions(self):
        """Test creating role with permissions"""
        role = RoleService.create_role(
            name='Manager',
            slug='manager',
            level=60,
            permission_names=['user.view', 'user.create']
        )
        
        self.assertIsNotNone(role)
        self.assertEqual(role.name, 'Manager')
        self.assertEqual(role.permissions.count(), 2)
        self.assertIn(self.permission1, role.permissions.all())
        self.assertIn(self.permission2, role.permissions.all())
    
    def test_update_role_permissions(self):
        """Test updating role permissions"""
        role = Role.objects.create(
            name='Editor',
            slug='editor',
            level=30
        )
        role.permissions.add(self.permission1)
        
        # Update permissions
        RoleService.update_role_permissions(
            role=role,
            permission_ids=[self.permission2.id] # type: ignore
        )
        
        self.assertEqual(role.permissions.count(), 1)
        self.assertIn(self.permission2, role.permissions.all())
        self.assertNotIn(self.permission1, role.permissions.all())
    
    def test_clone_role(self):
        """Test cloning a role"""
        original_role = Role.objects.create(
            name='Original',
            slug='original',
            level=40
        )
        original_role.permissions.add(self.permission1, self.permission2)
        
        cloned_role = RoleService.clone_role(
            role=original_role,
            new_name='Cloned',
            new_slug='cloned'
        )
        
        self.assertIsNotNone(cloned_role)
        self.assertEqual(cloned_role.name, 'Cloned')
        self.assertEqual(cloned_role.slug, 'cloned')
        self.assertEqual(cloned_role.level, original_role.level)
        self.assertEqual(
            cloned_role.permissions.count(),
            original_role.permissions.count()
        )
