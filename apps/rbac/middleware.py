"""
RBAC Middleware for automatic permission checking
"""
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin


class RBACMiddleware(MiddlewareMixin):
    """
    Middleware to check permissions based on URL patterns
    Configure in settings:
    
    RBAC_URL_PERMISSIONS = {
        '/api/users/': 'user.view',
        '/api/users/create/': 'user.create',
        '/api/admin/': 'admin.access',
    }
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return None
        
        # Get RBAC configuration from settings
        from django.conf import settings
        url_permissions = getattr(settings, 'RBAC_URL_PERMISSIONS', {})
        
        if not url_permissions:
            return None
        
        # Check if current path matches any configured patterns
        current_path = request.path
        
        for url_pattern, required_permission in url_permissions.items():
            if current_path.startswith(url_pattern):
                if not request.user.is_authenticated:
                    return JsonResponse(
                        {'error': 'Authentication required'},
                        status=401
                    )
                
                if not request.user.has_permission(required_permission):
                    return JsonResponse(
                        {'error': f'Permission "{required_permission}" required'},
                        status=403
                    )
        
        return None


class RoleExpirationMiddleware(MiddlewareMixin):
    """
    Middleware to check and update expired roles
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            from apps.rbac.models import UserRole
            from django.utils import timezone
            
            # Mark expired roles as inactive
            UserRole.objects.filter(
                user=request.user,
                is_active=True,
                expires_at__lte=timezone.now()
            ).update(is_active=False)
        
        return None
