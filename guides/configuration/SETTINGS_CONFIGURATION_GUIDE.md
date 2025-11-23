# Django Settings Configuration Guide

## Overview

This guide explains how to structure Django settings using a split configuration approach with separate files for different environments (base, local, docker, production) and how to configure DEBUG mode and frontend URLs from environment variables.

## Table of Contents

1. [Settings Structure](#settings-structure)
2. [Base Settings](#base-settings)
3. [Local Development Settings](#local-development-settings)
4. [Docker Settings](#docker-settings)
5. [Production Settings](#production-settings)
6. [Environment Variables Configuration](#environment-variables-configuration)
7. [Usage Instructions](#usage-instructions)
8. [Best Practices](#best-practices)

---

## Settings Structure

```
config/
├── __init__.py
├── asgi.py
├── wsgi.py
├── celery.py
├── urls.py
└── settings/
    ├── __init__.py
    ├── base.py           # Common settings for all environments
    ├── local.py          # Local development (without Docker)
    ├── docker.py         # Docker development environment
    └── production.py     # Production settings
```

---

## Base Settings

**File: `config/settings/base.py`**

This file contains all common settings shared across all environments.

### Key Features:
- ✅ Core Django configuration
- ✅ Installed apps (Django, DRF, Channels, Celery, Allauth)
- ✅ Middleware configuration
- ✅ Database settings from environment variables
- ✅ Authentication backends
- ✅ JWT configuration
- ✅ Celery configuration
- ✅ Django Channels configuration
- ✅ Static and Media files configuration
- ✅ Email configuration
- ✅ CORS settings from .env
- ✅ Django Allauth configuration
- ✅ REST Framework configuration

### Structure:

```python
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# This will be overridden in environment-specific settings
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts from environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    # REST Framework
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    
    # CORS
    'corsheaders',
    
    # Django Channels
    'channels',
    
    # Django Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # dj-rest-auth
    'dj_rest_auth',
    'dj_rest_auth.registration',
    
    # API Documentation
    'drf_spectacular',
    
    # Filtering
    'django_filters',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.authentication',
    'apps.core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Django Allauth
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Site ID for Django Allauth
SITE_ID = 1

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# =============================================================================
# DJANGO REST FRAMEWORK SETTINGS
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

# =============================================================================
# SIMPLE JWT SETTINGS
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': config('JWT_ROTATE_REFRESH_TOKENS', default=True, cast=bool),
    'BLACKLIST_AFTER_ROTATION': config('JWT_BLACKLIST_AFTER_ROTATION', default=True, cast=bool),
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =============================================================================
# DJANGO ALLAUTH SETTINGS
# =============================================================================
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}

# =============================================================================
# DJ-REST-AUTH SETTINGS
# =============================================================================
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_AUTH_COOKIE': 'auth-token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh-token',
}

# =============================================================================
# CORS SETTINGS
# =============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Frontend URL from environment
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# =============================================================================
# CSRF SETTINGS
# =============================================================================
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)

# =============================================================================
# REDIS SETTINGS
# =============================================================================
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_DB = config('REDIS_DB', default=0, cast=int)
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# =============================================================================
# CACHE SETTINGS
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'replycompass',
        'TIMEOUT': 300,
    }
}

# =============================================================================
# CELERY SETTINGS
# =============================================================================
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/2')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_RESULT_EXTENDED = True

# =============================================================================
# DJANGO CHANNELS SETTINGS
# =============================================================================
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# =============================================================================
# EMAIL SETTINGS
# =============================================================================
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@replycompass.com')
ADMIN_EMAIL = config('ADMIN_EMAIL', default='admin@replycompass.com')

# =============================================================================
# FILE UPLOAD SETTINGS
# =============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# =============================================================================
# API DOCUMENTATION (DRF Spectacular)
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'ReplyCompass API',
    'DESCRIPTION': 'API documentation for ReplyCompass application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = config('LOG_LEVEL', default='INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
```

---

## Local Development Settings

**File: `config/settings/local.py`**

Settings for local development without Docker (running directly on your machine).

```python
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

# Redis - Local Redis instance
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

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

print("🚀 Running in LOCAL development mode")
```

---

## Docker Settings

**File: `config/settings/docker.py`**

Settings for Docker development environment.

```python
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
REDIS_DB = config('REDIS_DB', default=0, cast=int)

# Cache - Docker Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'replycompass',
        'TIMEOUT': 300,
    }
}

# Celery - Docker Redis
CELERY_BROKER_URL = config(
    'CELERY_BROKER_URL',
    default=f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
)
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND',
    default=f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
)

# Channels - Docker Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
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

# Development-specific apps (optional in Docker)
if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
    ]

print(f"🐳 Running in DOCKER mode (DEBUG={DEBUG})")
```

---

## Production Settings

**File: `config/settings/production.py`**

Settings for production deployment.

```python
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts - Must be set in environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Security Settings - Strict for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS and Proxy Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Database - Production PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'ATOMIC_REQUESTS': True,
    }
}

# Redis - Production Redis (managed service recommended)
REDIS_HOST = config('REDIS_HOST')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_DB = config('REDIS_DB', default=0, cast=int)
REDIS_PASSWORD = config('REDIS_PASSWORD', default='')

# Redis URL with password
if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Cache - Production Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'replycompass_prod',
        'TIMEOUT': 600,
    }
}

# Celery - Production
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
    'max_retries': 3,
}

# Channels - Production
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 2000,
            'expiry': 15,
        },
    },
}

# Email - Production SMTP or service (SendGrid, Mailgun, etc.)
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Static files - WhiteNoise with compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = False

# Media files - Should use cloud storage (S3, GCS, etc.) in production
# Uncomment and configure for AWS S3
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_DEFAULT_ACL = 'public-read'
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }

# CORS - Production frontend URLs
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# Frontend URL
FRONTEND_URL = config('FRONTEND_URL')

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

# Admin URL (change from default /admin/)
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Sentry Integration for Error Tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config('ENVIRONMENT', default='production'),
    )

# Logging - Production level
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['django.request']['level'] = 'ERROR'

# REST Framework - Production settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
)

# Remove Django Extensions and Debug Toolbar
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [
    'django_extensions',
    'debug_toolbar',
]]

# Rate Limiting (using django-ratelimit or similar)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

print("🚀 Running in PRODUCTION mode")
```

---

## Environment Variables Configuration

### Complete `.env` File Structure

```bash
# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# Options: local, docker, production
DJANGO_SETTINGS_MODULE=config.settings.docker

# =============================================================================
# DEBUG MODE
# =============================================================================
# IMPORTANT: Set to False in production!
DEBUG=True

# =============================================================================
# DJANGO SETTINGS
# =============================================================================
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================
# Frontend application URL
FRONTEND_URL=http://localhost:3000

# CORS allowed origins (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# CSRF trusted origins (comma-separated)
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=replycompass_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# =============================================================================
# REDIS SETTINGS
# =============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# =============================================================================
# CELERY SETTINGS
# =============================================================================
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# =============================================================================
# EMAIL SETTINGS
# =============================================================================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@replycompass.com

# =============================================================================
# JWT SETTINGS
# =============================================================================
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ROTATE_REFRESH_TOKENS=True
JWT_BLACKLIST_AFTER_ROTATION=True

# =============================================================================
# GOOGLE OAUTH SETTINGS
# =============================================================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# =============================================================================
# SECURITY SETTINGS (Production)
# =============================================================================
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO

# =============================================================================
# SENTRY (Production Error Tracking)
# =============================================================================
SENTRY_DSN=

# =============================================================================
# AWS S3 (Production Media Storage)
# =============================================================================
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=
# AWS_S3_REGION_NAME=us-east-1
```

---

## Usage Instructions

### 1. Settings Module Selection

#### Method 1: Environment Variable (Recommended)

Set the `DJANGO_SETTINGS_MODULE` environment variable:

```bash
# In .env file
DJANGO_SETTINGS_MODULE=config.settings.docker

# Or export in terminal
export DJANGO_SETTINGS_MODULE=config.settings.local
```

#### Method 2: Manage.py Command Line

```bash
# Local development
python manage.py runserver --settings=config.settings.local

# Docker
python manage.py runserver --settings=config.settings.docker

# Production
python manage.py runserver --settings=config.settings.production
```

### 2. Update `config/settings/__init__.py`

```python
"""
Settings package initialization.
Automatically loads the appropriate settings module based on DJANGO_SETTINGS_MODULE.
"""
import os

# Default to docker settings if not specified
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.docker')
```

### 3. Update `manage.py`

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Default to docker settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.docker')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

### 4. Update `config/wsgi.py`

```python
"""
WSGI config for ReplyCompass project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
```

### 5. Update `config/asgi.py`

```python
"""
ASGI config for ReplyCompass project.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django_asgi_app = get_asgi_application()

# Import after Django setup
# from apps.core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(websocket_urlpatterns)
    # ),
})
```

### 6. Docker Compose Environment

Update `docker-compose.yml` to use docker settings:

```yaml
services:
  web:
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.docker
    # ... rest of config
```

---

## Best Practices

### 1. **Never Commit Secrets**
   - Always use environment variables for sensitive data
   - Keep `.env` in `.gitignore`
   - Use `.env.example` as a template

### 2. **Environment-Specific Overrides**
   - Keep common settings in `base.py`
   - Override only what's different in environment files
   - Use `from .base import *` at the top of each environment file

### 3. **Debug Mode**
   ```python
   # NEVER hardcode DEBUG=True in production
   DEBUG = config('DEBUG', default=False, cast=bool)
   ```

### 4. **Frontend URL Configuration**
   ```python
   # Always load from environment
   FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
   
   # Use in your code
   redirect_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
   ```

### 5. **CORS Configuration**
   ```python
   # Development - Allow specific origins
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:3000',
       'http://127.0.0.1:3000',
   ]
   
   # Production - Load from environment
   CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
   ```

### 6. **Security Headers**
   ```python
   # Development
   SECURE_SSL_REDIRECT = False
   SESSION_COOKIE_SECURE = False
   
   # Production
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   ```

### 7. **Database Connections**
   ```python
   # Use connection pooling in production
   'CONN_MAX_AGE': 600,  # 10 minutes
   'ATOMIC_REQUESTS': True,
   ```

### 8. **Logging Levels**
   - Local: `DEBUG`
   - Docker: `INFO`
   - Production: `WARNING` or `ERROR`

---

## Testing Different Settings

```bash
# Test local settings
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py check

# Test docker settings
DJANGO_SETTINGS_MODULE=config.settings.docker python manage.py check

# Test production settings
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
```

---

## Environment Detection

Add this utility to check current environment:

**File: `apps/core/utils.py`**

```python
from django.conf import settings
import os

def get_environment():
    """Get current environment name."""
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    
    if 'local' in settings_module:
        return 'local'
    elif 'docker' in settings_module:
        return 'docker'
    elif 'production' in settings_module:
        return 'production'
    return 'unknown'

def is_production():
    """Check if running in production."""
    return get_environment() == 'production'

def is_development():
    """Check if running in development."""
    return get_environment() in ['local', 'docker']
```

---

## Quick Reference

| Setting File | Use Case | DEBUG | Database | Redis |
|--------------|----------|-------|----------|-------|
| `base.py` | Common settings | From .env | From .env | From .env |
| `local.py` | Local dev (no Docker) | True | localhost | localhost |
| `docker.py` | Docker development | From .env | db (container) | redis (container) |
| `production.py` | Production | False | Production DB | Production Redis |

---

## Summary

This settings structure provides:

✅ **Separation of concerns** - Different settings for different environments
✅ **Environment-based configuration** - All settings from `.env`
✅ **DEBUG mode control** - Easily toggle DEBUG via environment variable
✅ **Frontend URL configuration** - Configure frontend URLs from `.env`
✅ **Security** - Strict security settings in production
✅ **Flexibility** - Easy to switch between environments
✅ **Best practices** - Following Django's recommended patterns

**Ready to implement? Let me know when you want to start coding!** 🚀
