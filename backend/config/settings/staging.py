import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    "testing.zirkusmond.de",
]

PAYMENT_USES_SSL = True

PAYMENT_HOST = "testing.zirkusmond.de"
PAYMENT_VARIANTS = {
    "default": ("payments.dummy.DummyProvider", {}),
    "paypal": (
        "payments.paypal.PaypalProvider",
        {
            "client_id": os.environ.get("PAYPAL_CLIENT_ID", ""),
            "secret": os.environ.get("PAYPAL_SECRET", ""),
            "endpoint": os.environ.get("PAYPAL_ENDPOINT", "https://api.sandbox.paypal.com"),
            "capture": True,
        },
    ),
    "stripe": (
        "reservations.payments.stripe_provider.StripeProviderV3",
        {
            "api_key": os.environ.get("STRIPE_TEST_TOKEN"),
            "endpoint_secret": os.environ.get("STRIPE_TEST_HOOK_TOKEN"),
            "secure_endpoint": False,
        },
    ),
}
