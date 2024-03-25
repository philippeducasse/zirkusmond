"""
https://docs.djangoproject.com/en/3.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import logging
import logging.config
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CUR_DIR = Path.cwd()
print('BASE_DIR: %s' % BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['192.168.178.28', '192.168.178.21', 'mondy.ableph.net',
                 '127.0.0.1', 'localhost', '192.168.188.154', '192.168.1.137',
                 'zirkusmond.de', 'www.zirkusmond.de', 'testing.zirkusmond.de']


# Application definition
INSTALLED_APPS = [
    'zirkusmond.events',
    'zirkusmond.gallery',
    'zirkusmond.zm',

    'markdownx',
    'payments',

    'easy_thumbnails',
    'image_cropping',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zirkusmond.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'zirkusmond/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
            'libraries': {
                 'markdown': 'zirkusmond.templatetags.markdown'
             }
        },
    },
]

ASGI_APPLICATION = 'zirkusmond.asgi.application'


from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS



PAYMENT_MODEL = 'events.ReservationPayment'
if DEBUG:
    PAYMENT_HOST = 'localhost:8000'
    PAYMENT_USES_SSL = False
    PAYMENT_VARIANTS =  {
        'default': ('payments.dummy.DummyProvider', {}),
        'paypal': ('payments.paypal.PaypalProvider', {
            'client_id': 'Ad_26WJhrD5hvWOIe4y9z2z2XV8d66D_SNPenIKlUazAJG3bhmQwZfyagXFdZ4ZL15KvVxnz6P5O7VaE',
            'secret': 'EC_3Evhzbfb1F_ZYCMNih4bH0Oj3U7sCRmvRCcmjAktzbsEMbgnF2_byg1n5FU6N708O2Mws6zjMupnS',
            'endpoint': 'https://api.sandbox.paypal.com',
            'capture': True}),
        'card payment': ('payments.stripe.StripeProvider', {
            'public_key': '',
            'secret_key': '',
            }),
        'coinbase': ('zirkusmond.CoinbasePaymentProvider.CoinbaseProvider', {
            'key': '970a25f6-5161-4f51-9c96-3819763cf56f'})
        }


else:
    PAYMENT_HOST = 'zirkusmond.de'
    PAYMENT_USES_SSL = True
    PAYMENT_VARIANTS = {
        'paypal': ('payments.paypal.PaypalProvider', {
           'client_id': 'AQuG7F5Z8riP9M6kXdz0jXMFPl-dYWxY6xLPg7X1iU2qmIA7tKFwosYA3r2Un_NKL42cwlhQkfkOjGM-',
           'secret': 'EIiUdLCQAB3P9cr2r0lybJunYuZ9VANhEnp3cdu-jOqj5GTwSa96m8Yf2SvsFcAxDD9CI6Qz8Q4SVOGV',
           'endpoint': 'https://api.paypal.com',
           'capture': True}),
        'card-payment': ('payments.stripe.StripeProvider', {
            'public_key': '',
            'secret_key': '',
            }),
        'coinbase': ('zirkusmond.CoinbasePaymentProvider.CoinbaseProvider', {
            'key': '970a25f6-5161-4f51-9c96-3819763cf56f'})
        }



EMAIL_HOST_USER = 'reservation@zirkusmond.de'
MAIL_HOST_CRED = os.environ.get("MAIL_HOST_CRED", "")
EMAIL_HOST = '162.19.152.5'
EMAIL_PORT = 465
EMAIL_USE_SSL = True


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': CUR_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'monddb',
            'USER': 'mond',
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': 'zm_db',
            'PORT': '5432',
    }}



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Berlin'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'zirkusmond/static']
#STATICFILES_DIRS = ['.']
STATIC_ROOT = CUR_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = CUR_DIR / 'media'



# Clear prev config
LOGGING_CONFIG = None

# Get loglevel from env
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'debug').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console',],
        },
    },
})
