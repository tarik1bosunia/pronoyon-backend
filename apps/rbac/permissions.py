"""
DRF Permission Classes for RBAC
"""
from rest_framework import permissions


class HasPermission(permissions.BasePermission):
    """
    Check if user has a specific permission
    Usage: permission_classes = [HasPermission]
           permission_required = 'user.create'
    """
    
    permission_required = None
    
    def has_permission(self, request, view):
        # Allow if user is authenticated and is superuser
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            # Get permission from view attribute
            permission = getattr(view, 'permission_required', self.permission_required)
            
            if not permission:
                return True
            
            return request.user.has_permission(permission)
        
        return False


class HasAnyPermission(permissions.BasePermission):
    """
    Check if user has any of the specified permissions
    Usage: permission_classes = [HasAnyPermission]
           permissions_required = ['user.create', 'user.update']
    """
    
    permissions_required = []
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            permissions = getattr(view, 'permissions_required', self.permissions_required)
            
            if not permissions:
                return True
            
            return request.user.has_any_permission(permissions)
        
        return False


class HasAllPermissions(permissions.BasePermission):
    """
    Check if user has all of the specified permissions
    Usage: permission_classes = [HasAllPermissions]
           permissions_required = ['user.create', 'user.update']
    """
    
    permissions_required = []
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            permissions = getattr(view, 'permissions_required', self.permissions_required)
            
            if not permissions:
                return True
            
            return request.user.has_all_permissions(permissions)
        
        return False


class HasRole(permissions.BasePermission):
    """
    Check if user has a specific role
    Usage: permission_classes = [HasRole]
           role_required = 'admin'
    """
    
    role_required = None
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            role = getattr(view, 'role_required', self.role_required)
            
            if not role:
                return True
            
            return request.user.has_role(role)
        
        return False


class HasAnyRole(permissions.BasePermission):
    """
    Check if user has any of the specified roles
    Usage: permission_classes = [HasAnyRole]
           roles_required = ['admin', 'moderator']
    """
    
    roles_required = []
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            roles = getattr(view, 'roles_required', self.roles_required)
            
            if not roles:
                return True
            
            return any(request.user.has_role(role) for role in roles)
        
        return False


class MinimumRoleLevel(permissions.BasePermission):
    """
    Check if user's role level meets minimum requirement
    Usage: permission_classes = [MinimumRoleLevel]
           minimum_role_level = 50  # Manager level
    """
    
    minimum_role_level = 0
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            min_level = getattr(view, 'minimum_role_level', self.minimum_role_level)
            user_level = request.user.get_role_level()
            
            return user_level >= min_level
        
        return False


class IsOwnerOrHasPermission(permissions.BasePermission):
    """
    Check if user is the owner or has specific permission
    Usage: permission_classes = [IsOwnerOrHasPermission]
           permission_required = 'resource.update'
    """
    
    permission_required = None
    owner_field = 'user'  # Field name that references the owner
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            
            # Check if user is owner
            owner_field = getattr(view, 'owner_field', self.owner_field)
            owner = getattr(obj, owner_field, None)
            
            if owner == request.user:
                return True
            
            # Check permission
            permission = getattr(view, 'permission_required', self.permission_required)
            
            if permission:
                return request.user.has_permission(permission)
        
        return False
