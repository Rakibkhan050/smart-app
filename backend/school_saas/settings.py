import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-secret')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS - Updated for mobile access
# For development: allows localhost + your local network IP
# For production: replace with your actual domain names
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    # Add your local IP address here (find with: ipconfig)
    # Example: '192.168.1.100',
    # Allows all hosts in development (remove in production!)
    '*',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    'channels',
    'storages',
    'django_celery_results',
    
    # CORS Headers for mobile/cross-origin requests
    'corsheaders',

    # Core Multi-Business SaaS Apps
    'accounts',
    'tenants',  # Business/Store Management
    'drivers',  # NEW: Driver Management System
    'users',    # NEW: User Management System
    'incidents',  # NEW: Incident Reporting System
    'notifications',
    
    # Business Operations
    'inventory',  # Multi-tenant product management
    'pos',  # Point of Sale
    'payments',  # Payment processing
    'receipts',
    
    # Customer & Delivery
    'crm',  # Customer management per business
    'delivery',  # Delivery tracking
    
    # Analytics & Finance
    'finance',  # Financial reports & commission tracking
]

# Use the custom accounts User model so users have the `role` field
AUTH_USER_MODEL = 'accounts.User'

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Celery Beat Schedule - Periodic Tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-low-stock-daily': {
        'task': 'inventory.tasks.check_low_stock_and_notify',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
        'options': {'expires': 3600}  # Task expires after 1 hour if not executed
    },
    'check-overdue-deliveries-daily': {
        'task': 'delivery.tasks.check_overdue_deliveries',
        'schedule': crontab(hour=10, minute=0),  # Run daily at 10 AM
        'options': {'expires': 3600}
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS Configuration for mobile/PWA access
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your local IP when testing on mobile:
    # "http://192.168.1.100:3000",
]

CORS_ALLOW_CREDENTIALS = True
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

ROOT_URLCONF = 'school_saas.urls'

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

WSGI_APPLICATION = 'school_saas.wsgi.application'
ASGI_APPLICATION = 'school_saas.asgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    # fallback to sqlite for local dev/testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.getenv('CHANNEL_LAYERS_REDIS', 'redis://redis:6379/1')],
        },
    },
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL'))
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL'))

# Static & Media
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# Storage (S3)
# Use moto for S3 emulation in test/dev mode; real S3 when AWS credentials provided
USE_S3_MOCK = os.getenv('USE_S3_MOCK', 'False') == 'True'
if USE_S3_MOCK:
    # Use moto for local S3 emulation (Docker service at http://moto:5000)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = 'testing'
    AWS_SECRET_ACCESS_KEY = 'testing'
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_ENDPOINT_URL = 'http://moto:5000'
    AWS_STORAGE_BUCKET_NAME = 'test-bucket'
else:
    # Real S3 configuration
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

# Email (SendGrid sample)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'admin@example.com')

# Web Push (VAPID)
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')

# Stripe (use stripe-mock for test/dev; set STRIPE_API_KEY and STRIPE_WEBHOOK_SECRET in .env for production)
USE_STRIPE_MOCK = os.getenv('USE_STRIPE_MOCK', 'False') == 'True'
if USE_STRIPE_MOCK:
    # stripe-mock Docker service at localhost:12111
    STRIPE_API_KEY = 'sk_test_mock'
    STRIPE_WEBHOOK_SECRET = 'whsec_test_mock'
    STRIPE_MOCK_URL = os.getenv('STRIPE_MOCK_URL', 'http://stripe-mock:12111')
else:
    # Real Stripe configuration
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    STRIPE_MOCK_URL = None

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Simple JWT settings (example)
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Simple logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}
