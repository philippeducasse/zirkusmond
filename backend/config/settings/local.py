import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'monddb'),
        'USER': os.environ.get('DB_USER', 'mond'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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
