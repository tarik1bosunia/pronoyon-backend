"""
Health check views for Docker monitoring
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Basic health check endpoint
    Returns 200 if service is up
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'replycompass',
    })


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check - verifies dependencies
    Returns 200 if all dependencies are accessible
    """
    status = {
        'status': 'ready',
        'checks': {}
    }
    http_status = 200

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status['checks']['database'] = 'failed'
        status['status'] = 'not_ready'
        http_status = 503

    # Check cache/redis
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            status['checks']['cache'] = 'ok'
        else:
            raise Exception("Cache value mismatch")
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        status['checks']['cache'] = 'failed'
        status['status'] = 'not_ready'
        http_status = 503

    return JsonResponse(status, status=http_status)


@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check - basic service health
    Returns 200 if service is alive
    """
    return JsonResponse({
        'status': 'alive',
        'service': 'replycompass',
    })
