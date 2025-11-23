"""
Local development settings.
Use this for development without Docker (running directly on your machine).
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Debug Toolbar Middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar Settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email Backend - Console (print emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database - Can use SQLite for quick local development
# Uncomment below to use SQLite instead of PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Or use PostgreSQL locally
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='replycompass_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Redis - Local Redis instance
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Cache - Local Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'replycompass_local',
        'TIMEOUT': 300,
    }
}

# Celery - Use local Redis
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously

# Channels - Local Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# CORS - Allow all origins in local development
CORS_ALLOW_ALL_ORIGINS = True

# Security Settings - Relaxed for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files - Use Whitenoise for local serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Frontend URL - Local development
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Allowed Hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Logging - More verbose in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Django Extensions - Shell Plus
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True

# REST Framework - Add browsable API in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',  # Browsable API
)

print("🚀 Running in LOCAL development mode")
