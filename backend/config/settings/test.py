import logging.config

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"

PAYMENT_HOST = "localhost:8000"
PAYMENT_USES_SSL = False
PAYMENT_VARIANTS = {
    "default": ("payments.dummy.DummyProvider", {}),
    "paypal": ("payments.dummy.DummyProvider", {}),
    "stripe": ("payments.dummy.DummyProvider", {}),
}

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        "formatters": {
            "console": {
                "format": "%(levelname)s [%(name)s] %(message)s",
            },
        },
        "loggers": {
            "": {"level": "WARNING", "handlers": ["console"]},
            "django.db.backends": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            "django.template": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            "PIL": {"level": "WARNING", "handlers": ["console"], "propagate": False},
        },
    }
)
