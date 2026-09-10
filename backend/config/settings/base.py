import logging.config
import os
from pathlib import Path

import sentry_sdk

from config.settings.logging_config import LOGGING
from config.settings.rest_framework_config import REST_FRAMEWORK  # noqa: F401
from config.settings.tinymce_config import TINYMCE_DEFAULT_CONFIG  # noqa: F401
from config.settings.unfold_config import UNFOLD  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # zirkusmond/backend

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

INSTALLED_APPS = [
    # unfold
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    # core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "corsheaders",
    "payments",
    "anymail",
    "tinymce",
    "rest_framework",
    # Zirkusmond apps
    "events",
    "shows",
    "reservations",
    "stats",
    "newsletter",
    "rentals",
    "homepage_elements",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "monddb"),
        "USER": os.environ.get("DB_USER", "mond"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
            "libraries": {},
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"

PAYMENT_MODEL = "reservations.ReservationPayment"

# Stripe configuration
STRIPE_TOKEN = os.environ.get("STRIPE_TOKEN") or os.environ.get(
    "STRIPE_TEST_TOKEN", ""
)
STRIPE_HOOK_TOKEN = os.environ.get("STRIPE_HOOK_TOKEN") or os.environ.get(
    "STRIPE_TEST_HOOK_TOKEN", ""
)

EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY": os.environ.get("BREVO_API_KEY", ""),
}
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "reservation@zirkusmond.de")

# Mailchimp
NEWSLETTER_TOKEN = os.environ.get("NEWSLETTER_TOKEN", "")
MAILCHIMP_SERVER_PREFIX = os.environ.get("MAILCHIMP_SERVER_PREFIX", "")
MAILCHIMP_AUDIENCE_ID = os.environ.get("MAILCHIMP_AUDIENCE_ID", "")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", BASE_DIR / "media")

LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)


# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat - cleanup abandoned payments every 6 hours
CELERY_BEAT_SCHEDULE = {
    "cleanup-abandoned-payments": {
        "task": "reservations.tasks.cleanup_abandoned_payments",
        "schedule": 3600.0,  # 6 hours
    },
}

# sentry
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN_BACKEND", ""),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
