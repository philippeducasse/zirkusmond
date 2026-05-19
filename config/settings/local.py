import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

PAYMENT_HOST = 'localhost:8000'
PAYMENT_USES_SSL = False
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {}),
    'paypal': ('payments.paypal.PaypalProvider', {
        'client_id': os.environ.get('PAYPAL_SANDBOX_CLIENT_ID', ''),
        'secret': os.environ.get('PAYPAL_SANDBOX_SECRET', ''),
        'endpoint': 'https://api.sandbox.paypal.com',
        'capture': True,
    }),
    'bank card': ('events.StripePaymentProvider.StripeProvider', {
        'secret_key': os.environ.get('STRIPE_TEST_TOKEN', ''),
    }),
}
