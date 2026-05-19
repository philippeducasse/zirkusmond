from .base import *

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
        'PASSWORD': '999927nfopfh8282yfmo3027dbwfpmz01q',
        'HOST': 'zm_db',
        'PORT': '5432',
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

PAYMENT_HOST = 'zirkusmond.de'
PAYMENT_USES_SSL = True
PAYMENT_VARIANTS = {
    'paypal': ('payments.paypal.PaypalProvider', {
        'client_id': 'AQuG7F5Z8riP9M6kXdz0jXMFPl-dYWxY6xLPg7X1iU2qmIA7tKFwosYA3r2Un_NKL42cwlhQkfkOjGM-',
        'secret': 'EIiUdLCQAB3P9cr2r0lybJunYuZ9VANhEnp3cdu-jOqj5GTwSa96m8Yf2SvsFcAxDD9CI6Qz8Q4SVOGV',
        'endpoint': 'https://api.paypal.com',
        'capture': True,
    }),
    'bank card': ('events.StripePaymentProvider.StripeProvider', {
        'secret_key': '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',
    }),
}
