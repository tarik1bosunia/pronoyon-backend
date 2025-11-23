"""
RBAC Models - Role, Permission, and UserRole
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """
    Permission model for granular access control
    Format: resource.action (e.g., 'user.create', 'post.delete')
    """
    
    # Permission categories
    CATEGORY_CHOICES = [
        ('user', 'User Management'),
        ('content', 'Content Management'),
        ('analytics', 'Analytics & Reports'),
        ('settings', 'Settings & Configuration'),
        ('billing', 'Billing & Payments'),
        ('support', 'Customer Support'),
        ('api', 'API Access'),
        ('admin', 'Administration'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Permission identifier (e.g., 'user.create', 'post.delete')"
    )
    codename = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-safe permission code"
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of what this permission allows"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='user'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rbac_permissions'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['codename']),
            models.Index(fields=['category']),
        ]
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def clean(self):
        """Validate permission name format"""
        if '.' not in self.name:
            raise ValidationError({
                'name': _('Permission name must be in format: resource.action (e.g., user.create)')
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Role(models.Model):
    """
    Role model for grouping permissions
    Supports role hierarchy and inheritance
    """
    
    # Role types
    ROLE_TYPE_CHOICES = [
        ('system', 'System Role'),
        ('custom', 'Custom Role'),
        ('temporary', 'Temporary Role'),
    ]
    
    # Pre-defined role levels
    ROLE_LEVEL_CHOICES = [
        (0, 'Guest'),
        (10, 'Basic User'),
        (20, 'Premium User'),
        (30, 'Moderator'),
        (40, 'Content Manager'),
        (50, 'Support Agent'),
        (60, 'Manager'),
        (70, 'Admin'),
        (80, 'Super Admin'),
        (90, 'System'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Role name (e.g., 'Admin', 'Content Manager')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-safe role identifier"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of role responsibilities and access level"
    )
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPE_CHOICES,
        default='custom'
    )
    level = models.IntegerField(
        choices=ROLE_LEVEL_CHOICES,
        default=10,
        help_text="Role hierarchy level (higher = more privileges)"
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True,
        help_text="Permissions granted to this role"
    )
    inherits_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_roles',
        help_text="Parent role to inherit permissions from"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role can be assigned to users"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Assign this role to new users by default"
    )
    max_users = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of users that can have this role (null = unlimited)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rbac_roles'
        ordering = ['-level', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    def get_all_permissions(self):
        """
        Get all permissions including inherited ones
        Returns a queryset of Permission objects
        """
        permissions = set(self.permissions.filter(is_active=True))
        
        # Add inherited permissions
        if self.inherits_from:
            permissions.update(self.inherits_from.get_all_permissions())
        
        return Permission.objects.filter(id__in=[p.id for p in permissions])
    
    def has_permission(self, permission_name):
        """
        Check if role has a specific permission (including inherited)
        
        Args:
            permission_name (str): Permission name (e.g., 'user.create')
        
        Returns:
            bool: True if role has the permission
        """
        return self.get_all_permissions().filter(name=permission_name).exists()
    
    def get_user_count(self):
        """Get number of users with this role"""
        return self.user_roles.filter(is_active=True).count()
    
    def can_assign_more_users(self):
        """Check if role can accept more users"""
        if self.max_users is None:
            return True
        return self.get_user_count() < self.max_users
    
    def clean(self):
        """Validate role configuration"""
        # Prevent circular inheritance
        if self.inherits_from:
            parent = self.inherits_from
            while parent:
                if parent == self:
                    raise ValidationError({
                        'inherits_from': _('Circular role inheritance detected')
                    })
                parent = parent.inherits_from
        
        # Only one default role per level
        if self.is_default:
            existing_default = Role.objects.filter(
                is_default=True,
                level=self.level
            ).exclude(pk=self.pk).exists()
            
            if existing_default:
                raise ValidationError({
                    'is_default': _('Another role at this level is already set as default')
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class UserRole(models.Model):
    """
    User-Role assignment with expiration and restrictions
    Allows users to have multiple roles with different contexts
    """
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role assignment is currently active"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary role for the user (used for display)"
    )
    assigned_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role expiration date (null = never expires)"
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context for role (e.g., workspace_id, project_id)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this role assignment"
    )
    
    class Meta:
        db_table = 'rbac_user_roles'
        ordering = ['-is_primary', '-assigned_at']
        unique_together = [['user', 'role', 'context']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
    
    def is_expired(self):
        """Check if role assignment has expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def clean(self):
        """Validate user role assignment"""
        # Check if role can accept more users
        if not self.pk and not self.role.can_assign_more_users():
            raise ValidationError({
                'role': _(f'Role "{self.role.name}" has reached maximum users limit')
            })
        
        # Only one primary role per user
        if self.is_primary:
            existing_primary = UserRole.objects.filter(
                user=self.user,
                is_primary=True,
                is_active=True
            ).exclude(pk=self.pk).exists()
            
            if existing_primary:
                raise ValidationError({
                    'is_primary': _('User already has a primary role')
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RoleHistory(models.Model):
    """
    Audit log for role changes
    """
    
    ACTION_CHOICES = [
        ('assigned', 'Role Assigned'),
        ('revoked', 'Role Revoked'),
        ('expired', 'Role Expired'),
        ('modified', 'Role Modified'),
    ]
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='role_history'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    performed_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_actions'
    )
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rbac_role_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['role', 'created_at']),
        ]
        verbose_name = 'Role History'
        verbose_name_plural = 'Role History'
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.role.name}"
