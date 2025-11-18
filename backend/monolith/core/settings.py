import os
from pathlib import Path
from urllib.parse import urlparse
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=Csv())

# Security check: do not allow running with the placeholder secret in production
if not DEBUG and (not SECRET_KEY or SECRET_KEY == 'FlipFlop'):
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY is not set or is using the insecure default. '
        'Set DJANGO_SECRET_KEY in environment for production.'
    )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',
    'apps.catalog',
    'apps.comments',
    'apps.user',
    'apps.cart',
    'apps.order',
    'apps.payment',
    ]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='').strip()
DATABASE_ENGINE = config('DATABASE_ENGINE', default='sqlite').strip().lower()

if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    scheme = parsed.scheme or ''
    if scheme.startswith('postgres'):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': (parsed.path or '/').lstrip('/') or config('POSTGRES_DB', default='postgres'),
                'USER': parsed.username or config('POSTGRES_USER', default='postgres'),
                'PASSWORD': parsed.password or config('POSTGRES_PASSWORD', default=''),
                'HOST': parsed.hostname or config('POSTGRES_HOST', default='localhost'),
                'PORT': str(parsed.port or config('POSTGRES_PORT', default='5432')),
            }
        }
    else:
        raise ImproperlyConfigured('Unsupported DATABASE_URL scheme. Only postgres is supported.')
elif DATABASE_ENGINE in {'postgres', 'postgresql', 'psql'}:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB', default='postgres'),
            'USER': config('POSTGRES_USER', default='postgres'),
            'PASSWORD': config('POSTGRES_PASSWORD', default=''),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
        }
    }
else:
    sqlite_path = config('DATABASE_PATH', default=str(BASE_DIR.parent.parent / 'databases' / 'db.sqlite3'))
    sqlite_path = Path(sqlite_path)
    try:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(sqlite_path),
        }
    }



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

AUTH_USER_MODEL = 'user.User'

EMAIL_BACKEND = config(
    'DJANGO_EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
DEFAULT_FROM_EMAIL = config('DJANGO_DEFAULT_FROM_EMAIL', default='no-reply@range-shop.local')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CORS_ALLOW_ALL_ORIGINS = True  
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings if needed
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

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Provide these via environment variables when enabling Stripe.
STRIPE_API_KEY = config('STRIPE_API_KEY', default=None)
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default=None)