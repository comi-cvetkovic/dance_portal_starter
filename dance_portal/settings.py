import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '1234'

DEBUG = True

ALLOWED_HOSTS = ["209.74.87.118", "5678danceportal.com", "www.5678danceportal.com", "127.0.0.1",
    "localhost",]

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("sr-latn", "Srpski"),
]

USE_I18N = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Required Django & custom apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dance_portal.urls'

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
                'core.context_processors.add_pending_club_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'dance_portal.wsgi.application'

# Redirects
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core/static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'danceportal',      # your database name
        'USER': 'danceuser',           # database user
        'PASSWORD': 'StrongPass123!', # database user password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / "db.sqlite3",
#         }
#     }

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
TIME_ZONE = 'UTC'
USE_TZ = True

# Default primary key field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email (⚠️ should use environment variables in production!)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "mihailo.serbia@gmail.com"
EMAIL_HOST_PASSWORD = "ucop wjps bidd xciz"  # Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

