"""
Custom exception handlers for consistent API error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that ensures all errors return JSON responses
    with a consistent structure.
    
    Response format:
    {
        "error": "Error type",
        "message": "Human-readable error message",
        "details": {...},  # Optional detailed error information
        "status_code": 400
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If DRF handled it, format the response consistently
    if response is not None:
        custom_response_data = {
            'error': exc.__class__.__name__,
            'message': str(exc),
            'status_code': response.status_code
        }
        
        # Add detailed validation errors if available
        if isinstance(exc, ValidationError) and hasattr(exc, 'detail'):
            custom_response_data['details'] = response.data
        elif hasattr(response, 'data') and isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['details'] = response.data
        
        response.data = custom_response_data
        return response
    
    # Handle database integrity errors (e.g., duplicate email)
    if isinstance(exc, IntegrityError):
        error_message = str(exc)
        
        # Parse common integrity error messages
        if 'duplicate key' in error_message.lower():
            if 'email' in error_message.lower():
                message = 'A user with this email already exists.'
                field_error = {'email': ['This email is already registered.']}
            else:
                message = 'This record already exists.'
                field_error = None
        elif 'foreign key' in error_message.lower():
            message = 'Referenced record does not exist.'
            field_error = None
        else:
            message = 'Database integrity error occurred.'
            field_error = None
        
        logger.error(f"IntegrityError: {error_message}", exc_info=True)
        
        response_data = {
            'error': 'IntegrityError',
            'message': message,
            'status_code': 400
        }
        
        if field_error:
            response_data['details'] = field_error
        
        return Response(response_data, status=400)
    
    # Handle Django's ObjectDoesNotExist
    if isinstance(exc, ObjectDoesNotExist):
        logger.warning(f"ObjectDoesNotExist: {str(exc)}")
        return Response({
            'error': 'NotFound',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }, status=404)
    
    # Handle Django's Http404
    if isinstance(exc, Http404):
        logger.warning(f"Http404: {str(exc)}")
        return Response({
            'error': 'NotFound',
            'message': str(exc) or 'The requested resource was not found.',
            'status_code': 404
        }, status=404)
    
    # Handle Django's PermissionDenied
    if isinstance(exc, PermissionDenied):
        logger.warning(f"PermissionDenied: {str(exc)}")
        return Response({
            'error': 'PermissionDenied',
            'message': str(exc) or 'You do not have permission to perform this action.',
            'status_code': 403
        }, status=403)
    
    # Handle any other unexpected exceptions
    logger.error(f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}", exc_info=True)
    
    return Response({
        'error': 'ServerError',
        'message': 'An unexpected error occurred. Please try again later.',
        'status_code': 500,
        'details': {
            'exception_type': exc.__class__.__name__,
            'exception_message': str(exc)
        }
    }, status=500)
