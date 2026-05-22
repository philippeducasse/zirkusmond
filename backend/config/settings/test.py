from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

PAYMENT_HOST = 'localhost:8000'
PAYMENT_USES_SSL = False
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {}),
    'paypal': ('payments.dummy.DummyProvider', {}),
    'bank card': ('payments.dummy.DummyProvider', {}),
}
