"""
Custom middleware for consistent error responses.
"""
import json
import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class JSONErrorMiddleware:
    """
    Middleware to ensure all errors are returned as JSON responses.
    This catches any exceptions that weren't handled by DRF's exception handler.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # If it's a server error (500) or bad request (400+) and not JSON
        if response.status_code >= 400:
            content_type = response.get('Content-Type', '')
            
            # If response is not JSON, convert it
            if 'application/json' not in content_type:
                # Check if it's an API endpoint
                if request.path.startswith('/api/') or request.path.startswith('/accounts/'):
                    logger.warning(
                        f"Non-JSON error response for API endpoint: {request.path} "
                        f"(Status: {response.status_code})"
                    )
                    
                    # Create consistent JSON error response
                    error_data = {
                        'error': 'ServerError' if response.status_code >= 500 else 'ClientError',
                        'message': self._get_error_message(response.status_code),
                        'status_code': response.status_code
                    }
                    
                    # Log the original response for debugging
                    if settings.DEBUG:
                        try:
                            error_data['debug_info'] = {
                                'path': request.path,
                                'method': request.method,
                            }
                        except Exception:
                            pass
                    
                    return JsonResponse(error_data, status=response.status_code)
        
        return response
    
    def _get_error_message(self, status_code):
        """Get user-friendly error message based on status code."""
        messages = {
            400: 'Bad request. Please check your input.',
            401: 'Authentication required.',
            403: 'You do not have permission to perform this action.',
            404: 'The requested resource was not found.',
            405: 'Method not allowed.',
            429: 'Too many requests. Please try again later.',
            500: 'An internal server error occurred.',
            502: 'Bad gateway. Please try again later.',
            503: 'Service temporarily unavailable.',
        }
        return messages.get(status_code, 'An error occurred.')
    
    def process_exception(self, request, exception):
        """
        Handle exceptions that weren't caught by the view.
        This is called when an exception is raised during request processing.
        """
        # Only handle API requests
        if not (request.path.startswith('/api/') or request.path.startswith('/accounts/')):
            return None
        
        logger.error(
            f"Unhandled exception in middleware: {exception.__class__.__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'path': request.path,
                'method': request.method,
            }
        )
        
        error_data = {
            'error': exception.__class__.__name__,
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': 500
        }
        
        if settings.DEBUG:
            error_data['details'] = {
                'exception_type': exception.__class__.__name__,
                'exception_message': str(exception),
                'path': request.path,
                'method': request.method,
            }
        
        return JsonResponse(error_data, status=500)
