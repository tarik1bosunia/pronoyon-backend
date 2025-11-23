"""
RBAC Selectors - Data access layer for RBAC queries
Selectors are pure functions that retrieve data from the database
"""
from django.db.models import QuerySet, Q, Prefetch
from django.utils import timezone
from typing import Optional, List
from .models import Permission, Role, UserRole, RoleHistory


class PermissionSelectors:
    """Selectors for Permission model queries"""
    
    @staticmethod
    def get_all_permissions() -> QuerySet:
        """Get all active permissions"""
        return Permission.objects.filter(is_active=True)
    
    @staticmethod
    def get_permission_by_name(name: str) -> Optional[Permission]:
        """Get permission by name"""
        try:
            return Permission.objects.get(name=name, is_active=True)
        except Permission.DoesNotExist:
            return None
    
    @staticmethod
    def get_permission_by_codename(codename: str) -> Optional[Permission]:
        """Get permission by codename"""
        try:
            return Permission.objects.get(codename=codename, is_active=True)
        except Permission.DoesNotExist:
            return None
    
    @staticmethod
    def get_permissions_by_category(category: str) -> QuerySet:
        """Get all permissions in a category"""
        return Permission.objects.filter(category=category, is_active=True)
    
    @staticmethod
    def get_permissions_by_names(names: List[str]) -> QuerySet:
        """Get multiple permissions by names"""
        return Permission.objects.filter(name__in=names, is_active=True)
    
    @staticmethod
    def get_permissions_grouped_by_category() -> dict:
        """Get permissions grouped by category"""
        permissions = Permission.objects.filter(is_active=True).order_by('category', 'name')
        grouped = {}
        for permission in permissions:
            if permission.category not in grouped:
                grouped[permission.category] = []
            grouped[permission.category].append(permission)
        return grouped
    
    @staticmethod
    def search_permissions(query: str) -> QuerySet:
        """Search permissions by name or description"""
        return Permission.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )


class RoleSelectors:
    """Selectors for Role model queries"""
    
    @staticmethod
    def get_all_roles() -> QuerySet:
        """Get all active roles"""
        return Role.objects.filter(is_active=True).prefetch_related('permissions')
    
    @staticmethod
    def get_role_by_slug(slug: str) -> Optional[Role]:
        """Get role by slug"""
        try:
            return Role.objects.prefetch_related('permissions').get(
                slug=slug, 
                is_active=True
            )
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    def get_role_by_name(name: str) -> Optional[Role]:
        """Get role by name"""
        try:
            return Role.objects.prefetch_related('permissions').get(
                name=name,
                is_active=True
            )
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    def get_roles_by_level(min_level: int = 0, max_level: int = 100) -> QuerySet:
        """Get roles within level range"""
        return Role.objects.filter(
            level__gte=min_level,
            level__lte=max_level,
            is_active=True
        ).order_by('level')
    
    @staticmethod
    def get_roles_by_type(role_type: str) -> QuerySet:
        """Get roles by type (system, custom, temporary)"""
        return Role.objects.filter(role_type=role_type, is_active=True)
    
    @staticmethod
    def get_default_role() -> Optional[Role]:
        """Get the default role for new users"""
        return Role.objects.filter(is_default=True, is_active=True).first()
    
    @staticmethod
    def get_role_hierarchy() -> QuerySet:
        """Get all roles ordered by hierarchy"""
        return Role.objects.filter(is_active=True).order_by('-level', 'name')
    
    @staticmethod
    def get_roles_inheriting_from(role: Role) -> QuerySet:
        """Get all roles that inherit from a given role"""
        return Role.objects.filter(inherits_from=role, is_active=True)
    
    @staticmethod
    def get_assignable_roles(max_level: Optional[int] = None) -> QuerySet:
        """Get roles that can be assigned (optionally filtered by max level)"""
        queryset = Role.objects.filter(is_active=True)
        if max_level is not None:
            queryset = queryset.filter(level__lte=max_level)
        return queryset.order_by('level')


class UserRoleSelectors:
    """Selectors for UserRole model queries"""
    
    @staticmethod
    def get_user_active_roles(user) -> QuerySet:
        """Get all active roles for a user"""
        return UserRole.objects.filter(
            user=user,
            is_active=True,
            role__is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).select_related('role').prefetch_related('role__permissions')
    
    @staticmethod
    def get_user_primary_role(user) -> Optional[UserRole]:
        """Get user's primary role"""
        return UserRoleSelectors.get_user_active_roles(user).filter(
            is_primary=True
        ).first()
    
    @staticmethod
    def get_user_roles_by_context(user, context: dict) -> QuerySet:
        """Get user roles filtered by context"""
        return UserRoleSelectors.get_user_active_roles(user).filter(
            context=context
        )
    
    @staticmethod
    def get_users_with_role(role: Role) -> QuerySet:
        """Get all users with a specific role"""
        return UserRole.objects.filter(
            role=role,
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).select_related('user')
    
    @staticmethod
    def get_users_with_permission(permission_name: str) -> QuerySet:
        """Get all users who have a specific permission"""
        permission = PermissionSelectors.get_permission_by_name(permission_name)
        if not permission:
            return UserRole.objects.none()
        
        roles_with_permission = permission.roles.filter(is_active=True)
        return UserRole.objects.filter(
            role__in=roles_with_permission,
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).select_related('user')
    
    @staticmethod
    def get_expired_user_roles() -> QuerySet:
        """Get all expired but still active user roles"""
        return UserRole.objects.filter(
            is_active=True,
            expires_at__lte=timezone.now()
        )
    
    @staticmethod
    def get_user_role_by_id(user_role_id: int) -> Optional[UserRole]:
        """Get user role by ID"""
        try:
            return UserRole.objects.select_related('user', 'role').get(
                id=user_role_id
            )
        except UserRole.DoesNotExist:
            return None
    
    @staticmethod
    def user_has_role(user, role_slug: str) -> bool:
        """Check if user has a specific role"""
        return UserRoleSelectors.get_user_active_roles(user).filter(
            Q(role__slug=role_slug) | Q(role__name=role_slug)
        ).exists()
    
    @staticmethod
    def get_user_permissions(user) -> QuerySet:
        """Get all permissions for a user from all their active roles"""
        active_roles = UserRoleSelectors.get_user_active_roles(user)
        permission_ids = set()
        
        for user_role in active_roles:
            role_permissions = user_role.role.get_all_permissions()
            permission_ids.update(role_permissions.values_list('id', flat=True))
        
        return Permission.objects.filter(id__in=permission_ids)


class RoleHistorySelectors:
    """Selectors for RoleHistory model queries"""
    
    @staticmethod
    def get_user_role_history(user, limit: Optional[int] = None) -> QuerySet:
        """Get role history for a user"""
        queryset = RoleHistory.objects.filter(user=user).select_related(
            'role', 'performed_by'
        ).order_by('-created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_role_history_by_action(action: str) -> QuerySet:
        """Get role history filtered by action"""
        return RoleHistory.objects.filter(action=action).select_related(
            'user', 'role', 'performed_by'
        ).order_by('-created_at')
    
    @staticmethod
    def get_recent_role_changes(days: int = 7) -> QuerySet:
        """Get recent role changes within specified days"""
        since = timezone.now() - timezone.timedelta(days=days)
        return RoleHistory.objects.filter(
            created_at__gte=since
        ).select_related('user', 'role', 'performed_by').order_by('-created_at')
    
    @staticmethod
    def get_role_assignments_by_performer(performer) -> QuerySet:
        """Get all role assignments performed by a user"""
        return RoleHistory.objects.filter(
            performed_by=performer,
            action='assigned'
        ).select_related('user', 'role').order_by('-created_at')
