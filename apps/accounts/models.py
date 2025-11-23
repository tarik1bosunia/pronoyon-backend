"""
Custom User Model with RBAC integration
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

if TYPE_CHECKING:
    from typing import TypeVar
    _CustomUser = TypeVar('_CustomUser', bound='CustomUser')


class CustomUserManager(BaseUserManager['CustomUser']):  # type: ignore[type-arg]
    """
    Custom user manager for email-based authentication
    """
    
    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> CustomUser:
        """Create and return a regular user"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> CustomUser:
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email as username and RBAC support
    """
    
    # Authentication fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        }
    )
    
    # Profile fields
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    # Status fields
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email address.'),
    )
    
    # Timestamps
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional user metadata"
    )
    
    objects: CustomUserManager = CustomUserManager()  # type: ignore[assignment]
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name or self.email.split('@')[0]
    
    # RBAC methods
    
    def get_active_roles(self):
        """Get all active roles for the user"""
        from apps.rbac.selectors import UserRoleSelectors
        return UserRoleSelectors.get_user_active_roles(self)
    
    def get_primary_role(self):
        """Get user's primary role"""
        from apps.rbac.selectors import UserRoleSelectors
        user_role = UserRoleSelectors.get_user_primary_role(self)
        
        if not user_role:
            # Fallback to highest level role
            active_roles = self.get_active_roles()
            user_role = active_roles.order_by('-role__level').first()
        
        return user_role.role if user_role else None
    
    def get_all_permissions(self):
        """Get all permissions from all active roles"""
        from apps.rbac.selectors import UserRoleSelectors
        return UserRoleSelectors.get_user_permissions(self)
    
    def has_role(self, role_name):
        """
        Check if user has a specific role
        
        Args:
            role_name (str): Role name or slug
        
        Returns:
            bool: True if user has the role
        """
        from apps.rbac.services import PermissionCheckService
        return PermissionCheckService.user_has_role(self, role_name)
    
    def has_permission(self, permission_name):
        """
        Check if user has a specific permission
        
        Args:
            permission_name (str): Permission name (e.g., 'user.create')
        
        Returns:
            bool: True if user has the permission
        """
        from apps.rbac.services import PermissionCheckService
        return PermissionCheckService.user_has_permission(self, permission_name)
    
    def has_any_permission(self, permission_names):
        """
        Check if user has any of the specified permissions
        
        Args:
            permission_names (list): List of permission names
        
        Returns:
            bool: True if user has at least one permission
        """
        from apps.rbac.services import PermissionCheckService
        return PermissionCheckService.user_has_any_permission(self, permission_names)
    
    def has_all_permissions(self, permission_names):
        """
        Check if user has all of the specified permissions
        
        Args:
            permission_names (list): List of permission names
        
        Returns:
            bool: True if user has all permissions
        """
        from apps.rbac.services import PermissionCheckService
        return PermissionCheckService.user_has_all_permissions(self, permission_names)
    
    def assign_role(self, role, assigned_by=None, expires_at=None, context=None, is_primary=False):
        """
        Assign a role to the user
        
        Args:
            role: Role instance or role slug
            assigned_by: User who assigned the role
            expires_at: Role expiration datetime
            context: Additional context dict
            is_primary: Whether this is the primary role
        
        Returns:
            UserRole instance
        """
        from apps.rbac.models import Role
        from apps.rbac.services import UserRoleService
        from apps.rbac.selectors import RoleSelectors
        
        if isinstance(role, str):
            role = RoleSelectors.get_role_by_slug(role)
            if not role:
                raise ValueError(f"Role '{role}' not found")
        
        return UserRoleService.assign_role_to_user(
            user=self,
            role=role,
            assigned_by=assigned_by,
            expires_at=expires_at,
            context=context,
            is_primary=is_primary
        )
    
    def revoke_role(self, role):
        """
        Revoke a role from the user
        
        Args:
            role: Role instance or role slug
        """
        from apps.rbac.services import UserRoleService
        UserRoleService.revoke_role_from_user(self, role)
    
    def get_role_level(self):
        """Get the highest role level for the user"""
        from apps.rbac.services import PermissionCheckService
        return PermissionCheckService.get_user_role_level(self)
