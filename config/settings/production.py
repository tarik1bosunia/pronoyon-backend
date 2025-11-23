# """
# Production settings for ReplyCompass.
# Use this for production deployment with strict security settings.
# """

# from .base import *
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# from sentry_sdk.integrations.celery import CeleryIntegration
# from sentry_sdk.integrations.redis import RedisIntegration

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False

# # Allowed hosts - Must be set in environment variable
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# # Security Settings - Strict for production
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# X_FRAME_OPTIONS = 'DENY'

# # HTTPS and Proxy Settings
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# # Session Security
# SESSION_COOKIE_AGE = 1209600  # 2 weeks
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_DOMAIN = config('SESSION_COOKIE_DOMAIN', default=None)

# # CSRF settings
# CSRF_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_DOMAIN = config('CSRF_COOKIE_DOMAIN', default=None)
# CSRF_USE_SESSIONS = False

# # Database - Production PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT', default='5432'),
#         'CONN_MAX_AGE': 600,
#         'OPTIONS': {
#             'sslmode': 'require',
#             'connect_timeout': 10,
#         },
#         'ATOMIC_REQUESTS': True,
#     }
# }

# # Redis - Production Redis (managed service recommended)
# REDIS_HOST = config('REDIS_HOST')
# REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
# REDIS_DB = config('REDIS_DB', default=0, cast=int)
# REDIS_PASSWORD = config('REDIS_PASSWORD', default='')

# # Redis URL with password
# if REDIS_PASSWORD:
#     REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
# else:
#     REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# # Cache - Production Redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {
#                 'max_connections': 100,
#                 'retry_on_timeout': True,
#             },
#             'SOCKET_CONNECT_TIMEOUT': 5,
#             'SOCKET_TIMEOUT': 5,
#         },
#         'KEY_PREFIX': 'replycompass_prod',
#         'TIMEOUT': 600,
#     }
# }

# # Celery - Production
# CELERY_BROKER_URL = config('CELERY_BROKER_URL')
# CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
# CELERY_BROKER_TRANSPORT_OPTIONS = {
#     'visibility_timeout': 3600,
#     'max_retries': 3,
# }
# CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# # Channels - Production
# if REDIS_PASSWORD:
#     CHANNEL_REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'
# else:
#     CHANNEL_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [CHANNEL_REDIS_URL],
#             'capacity': 2000,
#             'expiry': 15,
#         },
#     },
# }

# # Email - Production SMTP or service (SendGrid, Mailgun, etc.)
# EMAIL_BACKEND = config(
#     'EMAIL_BACKEND',
#     default='django.core.mail.backends.smtp.EmailBackend'
# )
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@replycompass.com')

# # Static files - WhiteNoise with compression
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# WHITENOISE_MANIFEST_STRICT = False
# WHITENOISE_ALLOW_ALL_ORIGINS = False

# # Media files - AWS S3 (recommended for production)
# # Uncomment and configure for AWS S3
# USE_S3 = config('USE_S3', default=False, cast=bool)

# if USE_S3:
#     # AWS S3 Settings
#     AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
#     AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
#     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#     AWS_DEFAULT_ACL = 'public-read'
#     AWS_S3_OBJECT_PARAMETERS = {
#         'CacheControl': 'max-age=86400',
#     }
#     AWS_LOCATION = 'media'
    
#     # Media files configuration
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

# # CORS - Production frontend URLs
# CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
# CORS_ALLOW_CREDENTIALS = True

# # Frontend URL
# FRONTEND_URL = config('FRONTEND_URL')

# # CSRF Trusted Origins
# CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

# # Admin URL (change from default /admin/ for security)
# ADMIN_URL = config('ADMIN_URL', default='admin/')

# # Sentry Integration for Error Tracking
# SENTRY_DSN = config('SENTRY_DSN', default='')
# SENTRY_ENVIRONMENT = config('ENVIRONMENT', default='production')

# if SENTRY_DSN:
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[
#             DjangoIntegration(),
#             CeleryIntegration(),
#             RedisIntegration(),
#         ],
#         traces_sample_rate=0.1,
#         send_default_pii=False,
#         environment=SENTRY_ENVIRONMENT,
#         # Set traces_sample_rate to 1.0 to capture 100%
#         # of transactions for performance monitoring.
#         # We recommend adjusting this value in production.
#     )

# # Logging - Production level
# LOGGING['root']['level'] = 'WARNING'
# LOGGING['loggers']['django']['level'] = 'WARNING'
# LOGGING['loggers']['django.request']['level'] = 'ERROR'
# LOGGING['loggers']['django.security']['level'] = 'ERROR'
# LOGGING['loggers']['celery']['level'] = 'WARNING'
# LOGGING['loggers']['apps']['level'] = 'INFO'

# # Add error notification handler for production
# LOGGING['handlers']['mail_admins'] = {
#     'level': 'ERROR',
#     'class': 'django.utils.log.AdminEmailHandler',
#     'include_html': True,
# }

# LOGGING['loggers']['django.request']['handlers'] = ['console', 'error_file', 'mail_admins']

# # Admin notification
# ADMINS = [
#     ('Admin', config('ADMIN_EMAIL', default='admin@replycompass.com')),
# ]

# MANAGERS = ADMINS

# # REST Framework - Production settings
# REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
#     'rest_framework.renderers.JSONRenderer',
# )

# # Remove development apps
# INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [
#     'django_extensions',
#     'debug_toolbar',
# ]]

# MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# # Rate Limiting (using django-ratelimit or similar)
# RATELIMIT_ENABLE = True
# RATELIMIT_USE_CACHE = 'default'

# # Django Axes - Protect against brute force attacks
# AXES_ENABLED = True
# AXES_FAILURE_LIMIT = 5
# AXES_COOLOFF_TIME = 1  # 1 hour
# AXES_LOCKOUT_TEMPLATE = 'account/lockout.html'

# # Password validation - Stricter in production
# AUTH_PASSWORD_VALIDATORS += [
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#         'OPTIONS': {
#             'min_length': 12,  # Stricter than base (8)
#         }
#     },
# ]

# # Data Upload - Limit upload size
# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
# FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# # Timeout settings
# CONN_MAX_AGE = 600
# REQUEST_TIMEOUT = 60

# print(f"🚀 Running in PRODUCTION mode (Environment: {SENTRY_ENVIRONMENT})")
