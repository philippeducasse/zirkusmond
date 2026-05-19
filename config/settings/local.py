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
        'client_id': 'Ad_26WJhrD5hvWOIe4y9z2z2XV8d66D_SNPenIKlUazAJG3bhmQwZfyagXFdZ4ZL15KvVxnz6P5O7VaE',
        'secret': 'EC_3Evhzbfb1F_ZYCMNih4bH0Oj3U7sCRmvRCcmjAktzbsEMbgnF2_byg1n5FU6N708O2Mws6zjMupnS',
        'endpoint': 'https://api.sandbox.paypal.com',
        'capture': True,
    }),
    'bank card': ('events.StripePaymentProvider.StripeProvider', {
        'secret_key': '',
    }),
}
