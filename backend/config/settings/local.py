import os

from .base import *

DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
FRONTEND_URL = "http://localhost:3000"

PAYMENT_HOST = "localhost:8000"
PAYMENT_USES_SSL = False
PAYMENT_VARIANTS = {
    "default": ("payments.dummy.DummyProvider", {}),
    "paypal": (
        "payments.paypal.PaypalProvider",
        {
            "client_id": os.environ["PAYPAL_SANDBOX_CLIENT_ID"],
            "secret": os.environ["PAYPAL_SANDBOX_SECRET"],
            "endpoint": "https://api.sandbox.paypal.com",
            "capture": True,
        },
    ),
    "stripe": (
        "reservations.payments.stripe_provider.TestStripeProvider",
        {
            "secret_key": os.environ.get("STRIPE_TEST_SECRET_KEY"),
        },
    ),
}
