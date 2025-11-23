"""
View Decorators for RBAC
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def permission_required(permission_name, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user has required permission
    
    Usage:
        @permission_required('user.create')
        def my_view(request):
            ...
    
    Args:
        permission_name (str): Permission name (e.g., 'user.create')
        raise_exception (bool): Raise PermissionDenied or redirect
        redirect_url (str): URL to redirect if permission denied
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            if request.user.is_superuser or request.user.has_permission(permission_name):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"Permission '{permission_name}' required")
            
            if redirect_url:
                messages.error(request, f"You don't have permission to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"Permission '{permission_name}' required")
        
        return wrapper
    return decorator


def any_permission_required(permission_names, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user has any of the required permissions
    
    Usage:
        @any_permission_required(['user.create', 'user.update'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            if request.user.is_superuser or request.user.has_any_permission(permission_names):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"One of these permissions required: {', '.join(permission_names)}")
            
            if redirect_url:
                messages.error(request, "You don't have permission to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"One of these permissions required: {', '.join(permission_names)}")
        
        return wrapper
    return decorator


def all_permissions_required(permission_names, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user has all of the required permissions
    
    Usage:
        @all_permissions_required(['user.create', 'user.delete'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            if request.user.is_superuser or request.user.has_all_permissions(permission_names):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"All of these permissions required: {', '.join(permission_names)}")
            
            if redirect_url:
                messages.error(request, "You don't have permission to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"All of these permissions required: {', '.join(permission_names)}")
        
        return wrapper
    return decorator


def role_required(role_name, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user has required role
    
    Usage:
        @role_required('admin')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            if request.user.is_superuser or request.user.has_role(role_name):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"Role '{role_name}' required")
            
            if redirect_url:
                messages.error(request, "You don't have the required role to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"Role '{role_name}' required")
        
        return wrapper
    return decorator


def any_role_required(role_names, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user has any of the required roles
    
    Usage:
        @any_role_required(['admin', 'moderator'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            has_role = any(request.user.has_role(role) for role in role_names)
            
            if request.user.is_superuser or has_role:
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"One of these roles required: {', '.join(role_names)}")
            
            if redirect_url:
                messages.error(request, "You don't have the required role to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"One of these roles required: {', '.join(role_names)}")
        
        return wrapper
    return decorator


def minimum_role_level(level, raise_exception=True, redirect_url=None):
    """
    Decorator to check if user's role level meets minimum requirement
    
    Usage:
        @minimum_role_level(50)  # Manager level
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect('login')
                raise PermissionDenied("Authentication required")
            
            user_level = request.user.get_role_level()
            
            if request.user.is_superuser or user_level >= level:
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied(f"Minimum role level {level} required")
            
            if redirect_url:
                messages.error(request, "You don't have sufficient role level to access this resource")
                return redirect(redirect_url)
            
            raise PermissionDenied(f"Minimum role level {level} required")
        
        return wrapper
    return decorator
