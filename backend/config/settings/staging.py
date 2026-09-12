import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["testing.zirkusmond.de", "localhost"]

PAYMENT_USES_SSL = True
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://testing.zirkusmond.de")
PAYMENT_HOST = "testing.zirkusmond.de"
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
