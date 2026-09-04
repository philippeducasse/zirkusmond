import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    "zirkusmond.de",
    "www.zirkusmond.de",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = ["https://zirkusmond.de", "https://www.zirkusmond.de"]

CORS_ALLOWED_ORIGINS = [
    "https://zirkusmond.de",
    "https://www.zirkusmond.de",
]
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"

PAYMENT_USES_SSL = True
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://zirkusmond.de")
PAYMENT_HOST = "zirkusmond.de"

# Mailchimp configuration
NEWSLETTER_TOKEN = os.environ.get("NEWSLETTER_TOKEN", "")
MAILCHIMP_SERVER_PREFIX = os.environ.get("MAILCHIMP_SERVER_PREFIX", "")
MAILCHIMP_AUDIENCE_ID = os.environ.get("MAILCHIMP_AUDIENCE_ID", "")
