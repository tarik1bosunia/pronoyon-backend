"""
Integration tests for the complete RBAC system
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.rbac.models import Permission, Role, UserRole
from apps.rbac.services import UserRoleService, PermissionCheckService

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser as User
else:
    User = get_user_model()


class RBACIntegrationTestCase(TestCase):
    """Integration tests for complete RBAC workflows"""
    
    def setUp(self):
        """Set up complete test scenario"""
        # Create users
        self.guest_user = User.objects.create_user(
            email='guest@example.com',
            password='GuestPass123!'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='UserPass123!'
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            password='ModPass123!'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!'
        )
        
        # Create permissions for different categories
        self.view_perm = Permission.objects.create(
            name='content.view',
            codename='content-view',
            category='content'
        )
        self.create_perm = Permission.objects.create(
            name='content.create',
            codename='content-create',
            category='content'
        )
        self.edit_perm = Permission.objects.create(
            name='content.edit',
            codename='content-edit',
            category='content'
        )
        self.delete_perm = Permission.objects.create(
            name='content.delete',
            codename='content-delete',
            category='content'
        )
        self.moderate_perm = Permission.objects.create(
            name='content.moderate',
            codename='content-moderate',
            category='content'
        )
        self.admin_perm = Permission.objects.create(
            name='admin.access',
            codename='admin-access',
            category='admin'
        )
        
        # Create hierarchical roles
        self.guest_role = Role.objects.create(
            name='Guest',
            slug='guest',
            level=0,
            role_type='system'
        )
        self.guest_role.permissions.add(self.view_perm)
        
        self.user_role = Role.objects.create(
            name='User',
            slug='user',
            level=10,
            role_type='system',
            inherits_from=self.guest_role
        )
        self.user_role.permissions.add(self.create_perm)
        
        self.moderator_role = Role.objects.create(
            name='Moderator',
            slug='moderator',
            level=30,
            role_type='system',
            inherits_from=self.user_role
        )
        self.moderator_role.permissions.add(self.edit_perm, self.moderate_perm)
        
        self.admin_role = Role.objects.create(
            name='Admin',
            slug='admin',
            level=70,
            role_type='system',
            inherits_from=self.moderator_role
        )
        self.admin_role.permissions.add(self.delete_perm, self.admin_perm)
        
        # Assign roles to users
        UserRoleService.assign_role_to_user(
            self.guest_user, self.guest_role, is_primary=True
        )
        UserRoleService.assign_role_to_user(
            self.regular_user, self.user_role, is_primary=True
        )
        UserRoleService.assign_role_to_user(
            self.moderator, self.moderator_role, is_primary=True
        )
        UserRoleService.assign_role_to_user(
            self.admin, self.admin_role, is_primary=True
        )
    
    def test_guest_permissions(self):
        """Test guest user has only view permission"""
        self.assertTrue(self.guest_user.has_permission('content.view'))
        self.assertFalse(self.guest_user.has_permission('content.create'))
        self.assertFalse(self.guest_user.has_permission('content.edit'))
        self.assertFalse(self.guest_user.has_permission('content.delete'))
        self.assertFalse(self.guest_user.has_permission('content.moderate'))
        self.assertFalse(self.guest_user.has_permission('admin.access'))
    
    def test_regular_user_permissions(self):
        """Test regular user has view and create permissions"""
        # Inherited from guest
        self.assertTrue(self.regular_user.has_permission('content.view'))
        # Own permission
        self.assertTrue(self.regular_user.has_permission('content.create'))
        # Not granted
        self.assertFalse(self.regular_user.has_permission('content.edit'))
        self.assertFalse(self.regular_user.has_permission('content.delete'))
        self.assertFalse(self.regular_user.has_permission('admin.access'))
    
    def test_moderator_permissions(self):
        """Test moderator has view, create, edit, and moderate permissions"""
        # Inherited from guest and user
        self.assertTrue(self.moderator.has_permission('content.view'))
        self.assertTrue(self.moderator.has_permission('content.create'))
        # Own permissions
        self.assertTrue(self.moderator.has_permission('content.edit'))
        self.assertTrue(self.moderator.has_permission('content.moderate'))
        # Not granted
        self.assertFalse(self.moderator.has_permission('content.delete'))
        self.assertFalse(self.moderator.has_permission('admin.access'))
    
    def test_admin_permissions(self):
        """Test admin has all permissions"""
        # All content permissions
        self.assertTrue(self.admin.has_permission('content.view'))
        self.assertTrue(self.admin.has_permission('content.create'))
        self.assertTrue(self.admin.has_permission('content.edit'))
        self.assertTrue(self.admin.has_permission('content.moderate'))
        self.assertTrue(self.admin.has_permission('content.delete'))
        # Admin permission
        self.assertTrue(self.admin.has_permission('admin.access'))
    
    def test_role_hierarchy_levels(self):
        """Test role levels are correctly assigned"""
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.guest_user), 0
        )
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.regular_user), 10
        )
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.moderator), 30
        )
        self.assertEqual(
            PermissionCheckService.get_user_role_level(self.admin), 70
        )
    
    def test_role_inheritance_chain(self):
        """Test role inheritance works correctly"""
        # Admin role should have permissions from all parent roles
        admin_permissions = self.admin_role.get_all_permissions()
        
        self.assertIn(self.view_perm, admin_permissions)  # From Guest
        self.assertIn(self.create_perm, admin_permissions)  # From User
        self.assertIn(self.edit_perm, admin_permissions)  # From Moderator
        self.assertIn(self.moderate_perm, admin_permissions)  # From Moderator
        self.assertIn(self.delete_perm, admin_permissions)  # Own
        self.assertIn(self.admin_perm, admin_permissions)  # Own
    
    def test_user_promotion_flow(self):
        """Test promoting user from one role to another"""
        # Create new user
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='NewPass123!'
        )
        
        # Start as guest
        UserRoleService.assign_role_to_user(
            new_user, self.guest_role, is_primary=True
        )
        self.assertTrue(new_user.has_permission('content.view'))
        self.assertFalse(new_user.has_permission('content.create'))
        
        # Promote to regular user
        UserRoleService.revoke_role_from_user(new_user, self.guest_role)
        UserRoleService.assign_role_to_user(
            new_user, self.user_role, is_primary=True
        )
        self.assertTrue(new_user.has_permission('content.view'))
        self.assertTrue(new_user.has_permission('content.create'))
        self.assertFalse(new_user.has_permission('content.edit'))
        
        # Promote to moderator
        UserRoleService.revoke_role_from_user(new_user, self.user_role)
        UserRoleService.assign_role_to_user(
            new_user, self.moderator_role, is_primary=True
        )
        self.assertTrue(new_user.has_permission('content.moderate'))
        self.assertFalse(new_user.has_permission('admin.access'))
    
    def test_multiple_roles(self):
        """Test user with multiple active roles"""
        # Create custom role with specific permission (valid level: 0, 10, 20, etc.)
        custom_role = Role.objects.create(
            name='Custom',
            slug='custom',
            level=10  # Changed from 5 to valid level (0, 10, 20, etc.)
        )
        custom_permission = Permission.objects.create(
            name='custom.action',
            codename='custom-action',
            category='user'
        )
        custom_role.permissions.add(custom_permission)
        
        # Assign custom role in addition to user role
        UserRoleService.assign_role_to_user(
            self.regular_user, custom_role
        )
        
        # User should have permissions from both roles
        self.assertTrue(self.regular_user.has_permission('content.view'))
        self.assertTrue(self.regular_user.has_permission('content.create'))
        self.assertTrue(self.regular_user.has_permission('custom.action'))
    
    def test_has_any_and_all_permissions(self):
        """Test checking multiple permissions at once"""
        # Admin has all content permissions
        self.assertTrue(
            self.admin.has_all_permissions([
                'content.view',
                'content.create',
                'content.edit',
                'content.delete'
            ])
        )
        
        # Moderator doesn't have all content permissions
        self.assertFalse(
            self.moderator.has_all_permissions([
                'content.view',
                'content.create',
                'content.delete'  # Don't have this
            ])
        )
        
        # Moderator has at least one of these
        self.assertTrue(
            self.moderator.has_any_permission([
                'content.delete',  # Don't have
                'content.moderate'  # Have this
            ])
        )
        
        # Guest doesn't have any of these
        self.assertFalse(
            self.guest_user.has_any_permission([
                'content.create',
                'content.edit',
                'admin.access'
            ])
        )
