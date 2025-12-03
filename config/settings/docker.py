"""
Docker development environment settings.
Use this when running the application in Docker containers.
"""

from .base import *

# DEBUG mode from environment variable
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed hosts for Docker
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0,web',
    cast=Csv()
)

# Database - Docker PostgreSQL container
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='replycompass_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='db'),  # Docker service name
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Redis - Docker Redis container
REDIS_HOST = config('REDIS_HOST', default='redis')  # Docker service name
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_PASSWORD = config('REDIS_PASSWORD', default='changeme')
REDIS_DB = config('REDIS_DB', default=0, cast=int)

# Build Redis URL with password if provided
if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    CELERY_BROKER_DEFAULT = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_RESULT_DEFAULT = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2'
else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    CELERY_BROKER_DEFAULT = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_RESULT_DEFAULT = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'

# Use REDIS_URL from environment if provided, otherwise use built URL
REDIS_URL = config('REDIS_URL', default=REDIS_URL)

# Cache - Docker Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'replycompass_docker',
        'TIMEOUT': 300,
    }
}

# Celery - Docker Redis
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=CELERY_BROKER_DEFAULT)
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_RESULT_DEFAULT)

# Channels - Docker Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# Email Backend - Console for Docker development
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# CORS - Configure from environment
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

# Frontend URL from environment
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)

# Security Settings - Moderate for Docker development
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging - INFO level for Docker
LOGGING['root']['level'] = config('LOG_LEVEL', default='INFO')
LOGGING['loggers']['django']['level'] = config('DJANGO_LOG_LEVEL', default='INFO')
LOGGING['loggers']['apps']['level'] = config('LOG_LEVEL', default='INFO')

# Silence autoreload debug messages
LOGGING['loggers']['django.utils.autoreload'] = {
    'level': 'INFO',
    'handlers': ['console'],
    'propagate': False,
}

# Development-specific apps (optional in Docker)
if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
    ]
    
    # Add browsable API in debug mode
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )

print(f"🐳 Running in DOCKER mode (DEBUG={DEBUG})")
