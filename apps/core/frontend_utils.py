"""
Utility functions for handling multiple frontend URLs and CORS.
"""

from django.conf import settings


def get_primary_frontend_url():
    """
    Get the primary/default frontend URL.
    Used for: email links, OAuth callbacks, default redirects.
    
    Returns:
        str: Primary frontend URL (e.g., 'http://localhost:3000')
    """
    return settings.FRONTEND_URL


def get_all_frontend_urls():
    """
    Get all configured frontend URLs.
    Used for: validation, multi-app support.
    
    Returns:
        list: List of all frontend URLs
    """
    return settings.FRONTEND_URLS


def is_valid_frontend_url(url):
    """
    Check if a URL is a valid/allowed frontend URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is in allowed frontends
    """
    return url in settings.FRONTEND_URLS


def get_frontend_redirect_url(path='', frontend_url=None):
    """
    Generate a frontend redirect URL with optional path.
    
    Args:
        path (str): Optional path to append (e.g., '/reset-password')
        frontend_url (str): Specific frontend URL to use (defaults to primary)
        
    Returns:
        str: Complete redirect URL
        
    Examples:
        >>> get_frontend_redirect_url('/reset-password')
        'http://localhost:3000/reset-password'
        
        >>> get_frontend_redirect_url('/dashboard', 'http://localhost:3001')
        'http://localhost:3001/dashboard'
    """
    base_url = frontend_url or settings.FRONTEND_URL
    
    # Remove trailing slash from base URL
    base_url = base_url.rstrip('/')
    
    # Ensure path starts with /
    if path and not path.startswith('/'):
        path = f'/{path}'
    
    return f'{base_url}{path}'


def get_frontend_url_by_type(app_type='user'):
    """
    Get frontend URL based on application type.
    Useful when you have multiple frontends for different purposes.
    
    Args:
        app_type (str): Type of frontend app ('user', 'admin', 'mobile', 'partner')
        
    Returns:
        str: Frontend URL for the specified app type
        
    Examples:
        >>> get_frontend_url_by_type('admin')
        'http://localhost:3001'
    """
    # Map app types to frontend URLs
    # This can be customized based on your environment variables
    frontend_map = {
        'user': settings.FRONTEND_URL,  # Primary/default
        'admin': settings.FRONTEND_URLS[1] if len(settings.FRONTEND_URLS) > 1 else settings.FRONTEND_URL,
        'mobile': settings.FRONTEND_URLS[2] if len(settings.FRONTEND_URLS) > 2 else settings.FRONTEND_URL,
        'partner': settings.FRONTEND_URLS[3] if len(settings.FRONTEND_URLS) > 3 else settings.FRONTEND_URL,
    }
    
    return frontend_map.get(app_type, settings.FRONTEND_URL)


def generate_email_verification_url(token, user_type='user'):
    """
    Generate email verification URL for different user types.
    
    Args:
        token (str): Verification token
        user_type (str): Type of user ('user', 'admin', 'partner')
        
    Returns:
        str: Complete verification URL
    """
    frontend_url = get_frontend_url_by_type(user_type)
    return get_frontend_redirect_url(f'/verify-email/{token}', frontend_url)


def generate_password_reset_url(token, user_type='user'):
    """
    Generate password reset URL for different user types.
    
    Args:
        token (str): Reset token
        user_type (str): Type of user ('user', 'admin', 'partner')
        
    Returns:
        str: Complete reset URL
    """
    frontend_url = get_frontend_url_by_type(user_type)
    return get_frontend_redirect_url(f'/reset-password/{token}', frontend_url)


def get_oauth_redirect_url(provider='google', user_type='user'):
    """
    Generate OAuth redirect URL based on provider and user type.
    
    Args:
        provider (str): OAuth provider ('google', 'github', etc.)
        user_type (str): Type of user ('user', 'admin')
        
    Returns:
        str: OAuth callback URL
    """
    frontend_url = get_frontend_url_by_type(user_type)
    return get_frontend_redirect_url(f'/auth/{provider}/callback', frontend_url)
