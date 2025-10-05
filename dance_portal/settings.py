import os
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv("/opt/dance_portal_starter/.env")

# ── Security & debug ────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "1234")  # TODO: set env var in prod
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    "91.98.154.49",                 # NEW VPS IP
    "5678danceportal.com",
    "www.5678danceportal.com",
    "127.0.0.1",
    "localhost",
]

# Django 4+ needs this when using IP/domain over HTTP/HTTPS
CSRF_TRUSTED_ORIGINS = [
    "http://91.98.154.49",
    "https://91.98.154.49",
    "https://5678danceportal.com",
    "https://www.5678danceportal.com",
]

# If you’ll terminate TLS at Nginx and proxy to Django, these are useful:
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ── Localization / i18n ─────────────────────────────────────────────────────────
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("sr-Latn", "Srpski"),
]
USE_I18N = True
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 1209600  # 2 weeks
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = "Lax"
LANGUAGE_COOKIE_ALLOW_GET = True

TIME_ZONE = "UTC"
USE_TZ = True

# LOCALE_PATHS = [ BASE_DIR / "locale" ]

# ── Apps & middleware ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_countries",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dance_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.add_pending_club_count",
            ],
        },
    },
]

WSGI_APPLICATION = "dance_portal.wsgi.application"

# ── Auth redirects ──────────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# ── Static & media ─────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Database ───────────────────────────────────────────────────────────────────
# Default: SQLite (quick start). To switch to Postgres, set USE_POSTGRES=1 and the vars below.
USE_POSTGRES = os.getenv("USE_POSTGRES", "0").lower() in ("1", "true", "yes")

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "danceportal"),
            "USER": os.getenv("POSTGRES_USER", "django"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "change-me"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Password validation ────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Email (consider env vars in production) ─────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "5678community.office@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "gwrxovatjbbiinzi")  # Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

