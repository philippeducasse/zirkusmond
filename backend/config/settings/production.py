import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    "zirkusmond.de",
    "www.zirkusmond.de",
]

PAYMENT_USES_SSL = True

PAYMENT_HOST = "zirkusmond.de"
PAYMENT_VARIANTS = {
    "paypal": (
        "payments.paypal.PaypalProvider",
        {
            "client_id": os.environ["PAYPAL_LIVE_CLIENT_ID"],
            "secret": os.environ["PAYPAL_LIVE_SECRET"],
            "endpoint": "https://api.paypal.com",
            "capture": True,
        },
    ),
    "stripe": (
        "reservations.payments.stripe_provider.StripeProviderV3",
        {
            "api_key": os.environ["STRIPE_LIVE_SECRET_KEY"],
            "endpoint_secret": os.environ["STRIPE_LIVE_WEBHOOK_SECRET"],
            "secure_endpoint": True,
        },
    ),
}
