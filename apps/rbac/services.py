"""
RBAC Services - Business logic layer for RBAC operations
Services handle business logic, validations, and orchestrate operations
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import Permission, Role, UserRole, RoleHistory
from .selectors import (
    PermissionSelectors,
    RoleSelectors,
    UserRoleSelectors,
    RoleHistorySelectors
)


class PermissionService:
    """Service for Permission business logic"""
    
    @staticmethod
    @transaction.atomic
    def create_permission(
        name: str,
        codename: str,
        description: str = "",
        category: str = "user",
        is_active: bool = True
    ) -> Permission:
        """
        Create a new permission
        
        Args:
            name: Permission name in format 'resource.action'
            codename: URL-safe permission code
            description: Human-readable description
            category: Permission category
            is_active: Active status
        
        Returns:
            Created Permission instance
        
        Raises:
            ValidationError: If permission data is invalid
        """
        permission = Permission(
            name=name,
            codename=codename,
            description=description,
            category=category,
            is_active=is_active
        )
        permission.full_clean()
        permission.save()
        
        return permission
    
    @staticmethod
    @transaction.atomic
    def update_permission(
        permission: Permission,
        **kwargs
    ) -> Permission:
        """
        Update an existing permission
        
        Args:
            permission: Permission instance to update
            **kwargs: Fields to update
        
        Returns:
            Updated Permission instance
        """
        for field, value in kwargs.items():
            if hasattr(permission, field):
                setattr(permission, field, value)
        
        permission.full_clean()
        permission.save()
        
        return permission
    
    @staticmethod
    @transaction.atomic
    def deactivate_permission(permission: Permission) -> Permission:
        """Deactivate a permission"""
        permission.is_active = False
        permission.save()
        return permission
    
    @staticmethod
    @transaction.atomic
    def bulk_create_permissions(permissions_data: List[Dict[str, Any]]) -> List[Permission]:
        """
        Bulk create permissions
        
        Args:
            permissions_data: List of permission data dicts
        
        Returns:
            List of created Permission instances
        """
        permissions = []
        for data in permissions_data:
            permission = Permission(**data)
            permission.full_clean()
            permissions.append(permission)
        
        return Permission.objects.bulk_create(permissions)


class RoleService:
    """Service for Role business logic"""
    
    @staticmethod
    @transaction.atomic
    def create_role(
        name: str,
        slug: str,
        description: str = "",
        role_type: str = "custom",
        level: int = 10,
        inherits_from: Optional[Role] = None,
        permission_ids: Optional[List[int]] = None,
        permission_names: Optional[List[str]] = None,
        is_active: bool = True,
        is_default: bool = False,
        max_users: Optional[int] = None
    ) -> Role:
        """
        Create a new role
        
        Args:
            name: Role name
            slug: URL-safe role identifier
            description: Role description
            role_type: Type (system, custom, temporary)
            level: Hierarchy level (0-90)
            inherits_from: Parent role for inheritance
            permission_ids: List of permission IDs to assign
            permission_names: List of permission names to assign
            is_active: Active status
            is_default: Default role for new users
            max_users: Maximum users allowed (None = unlimited)
        
        Returns:
            Created Role instance
        
        Raises:
            ValidationError: If role data is invalid
        """
        role = Role(
            name=name,
            slug=slug,
            description=description,
            role_type=role_type,
            level=level,
            inherits_from=inherits_from,
            is_active=is_active,
            is_default=is_default,
            max_users=max_users
        )
        role.full_clean()
        role.save()
        
        # Assign permissions by IDs
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        # Or assign by names
        elif permission_names:
            permissions = Permission.objects.filter(name__in=permission_names)
            role.permissions.set(permissions)
        
        return role
    
    @staticmethod
    @transaction.atomic
    def update_role(
        role: Role,
        permission_ids: Optional[List[int]] = None,
        **kwargs
    ) -> Role:
        """
        Update an existing role
        
        Args:
            role: Role instance to update
            permission_ids: Optional list of permission IDs to assign
            **kwargs: Fields to update
        
        Returns:
            Updated Role instance
        """
        for field, value in kwargs.items():
            if hasattr(role, field) and field != 'permissions':
                setattr(role, field, value)
        
        role.full_clean()
        role.save()
        
        # Update permissions if provided
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role
    
    @staticmethod
    @transaction.atomic
    def add_permissions_to_role(role: Role, permission_ids: List[int]) -> Role:
        """Add permissions to a role"""
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.add(*permissions)
        return role
    
    @staticmethod
    @transaction.atomic
    def remove_permissions_from_role(role: Role, permission_ids: List[int]) -> Role:
        """Remove permissions from a role"""
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.remove(*permissions)
        return role
    
    @staticmethod
    @transaction.atomic
    def deactivate_role(role: Role) -> Role:
        """
        Deactivate a role
        Also deactivates all user role assignments
        """
        role.is_active = False
        role.save()
        
        # Deactivate all user assignments
        UserRole.objects.filter(role=role, is_active=True).update(is_active=False)
        
        return role
    
    @staticmethod
    def get_role_effective_permissions(role: Role) -> List[Permission]:
        """Get all permissions including inherited ones"""
        return list(role.get_all_permissions())
    
    @staticmethod
    def check_role_can_accept_users(role: Role) -> bool:
        """Check if role can accept more users"""
        return role.can_assign_more_users()
    
    @staticmethod
    @transaction.atomic
    def clone_role(role: Role, new_name: str, new_slug: str) -> Role:
        """
        Clone an existing role with a new name
        
        Args:
            role: Role to clone
            new_name: Name for the cloned role
            new_slug: Slug for the cloned role
        
        Returns:
            Cloned Role instance
        """
        # Get current permissions
        permission_ids = list(role.permissions.values_list('id', flat=True))
        
        # Create new role with same settings
        cloned_role = RoleService.create_role(
            name=new_name,
            slug=new_slug,
            description=f"Cloned from {role.name}",
            role_type=role.role_type,
            level=role.level,
            inherits_from=role.inherits_from,
            permission_ids=permission_ids,
            is_active=role.is_active,
            is_default=False,  # Never clone as default
            max_users=role.max_users
        )
        
        return cloned_role
    
    @staticmethod
    @transaction.atomic
    def update_role_permissions(role: Role, permission_ids: List[int]) -> Role:
        """
        Update role permissions (replaces all existing permissions)
        
        Args:
            role: Role instance
            permission_ids: List of permission IDs to assign
        
        Returns:
            Updated Role instance
        """
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        return role


class UserRoleService:
    """Service for UserRole business logic"""
    
    @staticmethod
    @transaction.atomic
    def assign_role_to_user(
        user,
        role: Role,
        assigned_by=None,
        expires_at: Optional[datetime] = None,
        context: Optional[Dict] = None,
        is_primary: bool = False,
        notes: str = ""
    ) -> UserRole:
        """
        Assign a role to a user
        
        Args:
            user: User instance
            role: Role instance
            assigned_by: User who performed the assignment
            expires_at: Optional expiration datetime
            context: Optional context dict (workspace_id, etc.)
            is_primary: Whether this is the primary role
            notes: Optional notes about the assignment
        
        Returns:
            UserRole instance
        
        Raises:
            ValidationError: If assignment is invalid
        """
        # Check if role can accept more users
        if not role.can_assign_more_users():
            raise ValidationError(
                f'Role "{role.name}" has reached maximum users limit'
            )
        
        # Get or create user role
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            context=context or {},
            defaults={
                'assigned_by': assigned_by,
                'expires_at': expires_at,
                'is_primary': is_primary,
                'notes': notes,
                'is_active': True
            }
        )
        
        # If exists, update it
        if not created:
            user_role.is_active = True
            user_role.expires_at = expires_at
            user_role.is_primary = is_primary
            if assigned_by:
                user_role.assigned_by = assigned_by
            if notes:
                user_role.notes = notes
            user_role.save()
        
        # If primary, remove primary from other roles
        if is_primary:
            UserRole.objects.filter(
                user=user,
                is_primary=True,
                is_active=True
            ).exclude(id=user_role.id).update(is_primary=False) # type: ignore
        
        return user_role
    
    @staticmethod
    @transaction.atomic
    def revoke_role_from_user(user, role: Role) -> bool:
        """
        Revoke a role from a user
        
        Args:
            user: User instance
            role: Role instance or slug
        
        Returns:
            True if role was revoked, False if not found
        """
        if isinstance(role, str):
            role_obj = RoleSelectors.get_role_by_slug(role)
            if not role_obj:
                return False
            role = role_obj
        
        updated = UserRole.objects.filter(
            user=user,
            role=role,
            is_active=True
        ).update(is_active=False)
        
        return updated > 0
    
    @staticmethod
    @transaction.atomic
    def set_primary_role(user_role: UserRole) -> UserRole:
        """
        Set a user role as primary
        
        Args:
            user_role: UserRole instance to set as primary
        
        Returns:
            Updated UserRole instance
        """
        # Remove primary from other roles
        UserRole.objects.filter(
            user=user_role.user,
            is_primary=True,
            is_active=True
        ).exclude(id=user_role.id).update(is_primary=False) # type: ignore
        
        # Set this as primary
        user_role.is_primary = True
        user_role.save()
        
        return user_role
    
    @staticmethod
    @transaction.atomic
    def extend_role_expiration(
        user_role: UserRole,
        new_expiration: datetime
    ) -> UserRole:
        """
        Extend role expiration date
        
        Args:
            user_role: UserRole instance
            new_expiration: New expiration datetime
        
        Returns:
            Updated UserRole instance
        """
        user_role.expires_at = new_expiration
        user_role.save()
        
        return user_role
    
    @staticmethod
    @transaction.atomic
    def bulk_assign_role(
        users: List,
        role: Role,
        assigned_by=None,
        expires_at: Optional[datetime] = None
    ) -> List[UserRole]:
        """
        Assign a role to multiple users
        
        Args:
            users: List of User instances
            role: Role instance
            assigned_by: User who performed the assignments
            expires_at: Optional expiration datetime
        
        Returns:
            List of created/updated UserRole instances
        """
        user_roles = []
        
        for user in users:
            user_role = UserRoleService.assign_role_to_user(
                user=user,
                role=role,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            user_roles.append(user_role)
        
        return user_roles
    
    @staticmethod
    @transaction.atomic
    def expire_user_roles() -> int:
        """
        Mark expired user roles as inactive
        
        Returns:
            Number of roles expired
        """
        expired_roles = UserRoleSelectors.get_expired_user_roles()
        count = expired_roles.count()
        
        expired_roles.update(is_active=False)
        
        # Create history entries
        for user_role in expired_roles:
            RoleHistory.objects.create(
                user=user_role.user,
                role=user_role.role,
                action='expired',
                reason='Role expired automatically',
                metadata={
                    'expired_at': timezone.now().isoformat(),
                    'context': user_role.context
                }
            )
        
        return count


class PermissionCheckService:
    """Service for permission checking logic"""
    
    @staticmethod
    def user_has_permission(user, permission_name: str) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user: User instance
            permission_name: Permission name
        
        Returns:
            True if user has permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Get user's permissions
        user_permissions = UserRoleSelectors.get_user_permissions(user)
        return user_permissions.filter(name=permission_name).exists()
    
    @staticmethod
    def user_has_any_permission(user, permission_names: List[str]) -> bool:
        """Check if user has any of the specified permissions"""
        if user.is_superuser:
            return True
        
        user_permissions = UserRoleSelectors.get_user_permissions(user)
        return user_permissions.filter(name__in=permission_names).exists()
    
    @staticmethod
    def user_has_all_permissions(user, permission_names: List[str]) -> bool:
        """Check if user has all of the specified permissions"""
        if user.is_superuser:
            return True
        
        user_permissions = UserRoleSelectors.get_user_permissions(user)
        user_permission_names = set(user_permissions.values_list('name', flat=True))
        return set(permission_names).issubset(user_permission_names)
    
    @staticmethod
    def user_has_role(user, role_identifier: str) -> bool:
        """
        Check if user has a specific role
        
        Args:
            user: User instance
            role_identifier: Role name or slug
        
        Returns:
            True if user has role
        """
        return UserRoleSelectors.user_has_role(user, role_identifier)
    
    @staticmethod
    def get_user_role_level(user) -> int:
        """
        Get user's highest role level
        
        Args:
            user: User instance
        
        Returns:
            Highest role level (0-90)
        """
        active_roles = UserRoleSelectors.get_user_active_roles(user)
        if not active_roles.exists():
            return 0
        
        return max(ur.role.level for ur in active_roles)
    
    @staticmethod
    def user_meets_minimum_level(user, minimum_level: int) -> bool:
        """Check if user's role level meets minimum requirement"""
        if user.is_superuser:
            return True
        
        user_level = PermissionCheckService.get_user_role_level(user)
        return user_level >= minimum_level


class RoleAnalyticsService:
    """Service for RBAC analytics and reporting"""
    
    @staticmethod
    def get_role_distribution() -> Dict[str, int]:
        """Get distribution of users across roles"""
        distribution = {}
        
        roles = RoleSelectors.get_all_roles()
        for role in roles:
            count = UserRoleSelectors.get_users_with_role(role).count()
            distribution[role.name] = count
        
        return distribution
    
    @staticmethod
    def get_permission_usage() -> Dict[str, int]:
        """Get number of users with each permission"""
        usage = {}
        
        permissions = PermissionSelectors.get_all_permissions()
        for permission in permissions:
            count = UserRoleSelectors.get_users_with_permission(permission.name).count()
            usage[permission.name] = count
        
        return usage
    
    @staticmethod
    def get_user_role_summary(user) -> Dict[str, Any]:
        """Get comprehensive role summary for a user"""
        active_roles = UserRoleSelectors.get_user_active_roles(user)
        primary_role = UserRoleSelectors.get_user_primary_role(user)
        permissions = UserRoleSelectors.get_user_permissions(user)
        
        return {
            'user': user,
            'roles': list(active_roles),
            'primary_role': primary_role.role if primary_role else None,
            'role_count': active_roles.count(),
            'permissions': list(permissions),
            'permission_count': permissions.count(),
            'role_level': PermissionCheckService.get_user_role_level(user),
            'is_superuser': user.is_superuser
        }
