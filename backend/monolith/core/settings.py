import os
from pathlib import Path
from urllib.parse import urlparse
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Basic secrets & debug
SECRET_KEY = config('DJANGO_SECRET_KEY', default='FlipFlop')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

# Hosts
# Default includes localhost variants; you can override via DJANGO_ALLOWED_HOSTS env var (comma separated)
ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0,range-lvzt.onrender.com',
    cast=Csv()
)

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

    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',

    # Your apps
    'apps.catalog',
    'apps.comments',
    'apps.user',
    'apps.cart',
    'apps.order',
    'apps.payment',
]

# MIDDLEWARE order:
# - corsheaders.middleware.CorsMiddleware should be as high as possible (before any middleware that can generate responses)
# - SecurityMiddleware should remain early
# - If using WhiteNoise (serving static files), it should come after SecurityMiddleware but after CorsMiddleware as well.
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

# Database configuration (supports DATABASE_URL for postgres)
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
                'PORT': str(parsed.port or config('POSTGRES_PORT', default='5432')) or '5432',
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

# FRONTEND URL (used for CSRF trusted origins / convenience)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# ---- CORS / CSRF configuration ----
# Known frontend and render host -- user confirmed these:
FRONTEND_ORIGIN = config('FRONTEND_URL', default='https://range-lemon.vercel.app')
RENDER_BACKEND_HOST = 'https://range-lvzt.onrender.com'

# Base CORS allowed origins list: include common local dev urls and the Vercel frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add FRONTEND and backend origins if present and not already in list
if FRONTEND_ORIGIN and FRONTEND_ORIGIN not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)

if RENDER_BACKEND_HOST and RENDER_BACKEND_HOST not in CORS_ALLOWED_ORIGINS:
    # backend origin doesn't usually need to be in allowed origins for browser requests,
    # but adding it won't hurt and can simplify some cross-origin flows (e.g. if you test from other origins).
    CORS_ALLOWED_ORIGINS.append(RENDER_BACKEND_HOST)

# In DEBUG you may choose to allow all origins for convenience; not recommended in production
if DEBUG:
    # recommended: still keep explicit origins, but for rapid dev set this True if you like
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True

# Allow common headers & methods used by fetch/XHR
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
    'referer',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# If your frontend is at a hostname that uses HTTPS and you want cookies & CSRF to work,
# add the frontend origin(s) to CSRF_TRUSTED_ORIGINS and to the CORS list above.
# Django expects scheme included (since Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    FRONTEND_ORIGIN,
    RENDER_BACKEND_HOST,
]

# Some deployment settings helpful for Render / proxies
# If Render or another proxy terminates SSL and forwards with X-Forwarded-Proto header:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# In production, you may want to set:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = 'Lax' or 'None' (if cross-site cookies are required)
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    # If you need cross-site cookies (frontend on different domain) set same site to None and allow credentials
    SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='None')
    CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='None')
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (you can enable WhiteNoise if desired)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe (optional)
STRIPE_API_KEY = config('STRIPE_API_KEY', default=None)
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default=None)
