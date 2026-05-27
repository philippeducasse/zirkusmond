import os
from .base import *

IS_TESTING = 'IS_TESTING' in os.environ

DEBUG = False
ALLOWED_HOSTS = [
    'zirkusmond.de',
    'www.zirkusmond.de',
    'testing.zirkusmond.de',
    'www.testing.zirkusmond.de',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monddb',
        'USER': 'mond',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'testing_postgres' if IS_TESTING else 'postgres',
        'PORT': '5432',
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

PAYMENT_USES_SSL = True

if IS_TESTING:
    PAYMENT_HOST = 'testing.zirkusmond.de'
    PAYMENT_VARIANTS = {
        'default': ('payments.dummy.DummyProvider', {}),
        'paypal': ('payments.paypal.PaypalProvider', {
            'client_id': os.environ['PAYPAL_SANDBOX_CLIENT_ID'],
            'secret': os.environ['PAYPAL_SANDBOX_SECRET'],
            'endpoint': 'https://api.sandbox.paypal.com',
            'capture': True,
        }),
        'stripe': ('reservations.payments.stripe_provider.StripeProviderV3', {
            'api_key': os.environ['STRIPE_TEST_TOKEN'],
            'endpoint_secret': os.environ.get('STRIPE_TEST_HOOK_TOKEN', ''),
            'secure_endpoint': True,
        }),
    }
else:
    PAYMENT_HOST = 'zirkusmond.de'
    PAYMENT_VARIANTS = {
        'paypal': ('payments.paypal.PaypalProvider', {
            'client_id': os.environ['PAYPAL_LIVE_CLIENT_ID'],
            'secret': os.environ['PAYPAL_LIVE_SECRET'],
            'endpoint': 'https://api.paypal.com',
            'capture': True,
        }),
        'stripe': ('reservations.payments.stripe_provider.StripeProviderV3', {
            'api_key': os.environ['STRIPE_LIVE_SECRET_KEY'],
            'endpoint_secret': os.environ['STRIPE_LIVE_WEBHOOK_SECRET'],
            'secure_endpoint': True,
        }),
    }
