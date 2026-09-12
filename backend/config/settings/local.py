from .base import *

DEBUG = True

# django-debug-toolbar is a dev-only dependency (not installed in staging/prod images),
# so it's added here rather than in base.py.
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:3000"]
FRONTEND_URL = "http://localhost:3000"

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True

PAYMENT_HOST = "localhost:8000"
PAYMENT_USES_SSL = False

# Celery - eager mode for local testing (tasks run synchronously, no broker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
