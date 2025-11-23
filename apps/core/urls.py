"""
Health check URL configuration
"""
from django.urls import path
from apps.core.health import health_check, readiness_check, liveness_check

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('ready/', readiness_check, name='readiness-check'),
    path('live/', liveness_check, name='liveness-check'),
]
