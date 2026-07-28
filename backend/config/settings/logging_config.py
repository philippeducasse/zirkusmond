import os

LOGLEVEL = os.getenv("DJANGO_LOGLEVEL", "debug").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": LOGLEVEL,
            "handlers": ["console"],
        },
        "django.db.backends": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.utils.autoreload": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}