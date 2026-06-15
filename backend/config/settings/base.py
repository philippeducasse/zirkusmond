import logging
import logging.config
import os
from pathlib import Path

from django.templatetags.static import static
from easy_thumbnails.conf import Settings as ThumbnailSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # zirkusmond/backend

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

INSTALLED_APPS = [
    # django core && unfold
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "payments",
    "anymail",
    "easy_thumbnails",
    "image_cropping",
    "tinymce",
    # Zirkusmond apps
    "events",
    "shows",
    "reservations",
    "stats",
    "newsletter",
    "rentals",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "monddb"),
        "USER": os.environ.get("DB_USER", "mond"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
            "libraries": {},
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"

THUMBNAIL_PROCESSORS = (
    "image_cropping.thumbnail_processors.crop_corners",
) + ThumbnailSettings.THUMBNAIL_PROCESSORS

PAYMENT_MODEL = "reservations.ReservationPayment"

EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY": os.environ.get("BREVO_API_KEY", ""),
}
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "reservation@zirkusmond.de")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", BASE_DIR / "media")

LOGGING_CONFIG = None
LOGLEVEL = os.getenv("DJANGO_LOGLEVEL", "debug").upper()

logging.config.dictConfig(
    {
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
)

TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "960px",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
}


UNFOLD = {
    "SITE_TITLE": "Zirkusmond admin panel",
    "SITE_HEADER": "Zirkusmond",
    "SITE_SUBHEADER": "Admin Panel",
    "SITE_ICON": lambda request: static("media/images/gallery/logo.png"),
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("media/images/gallery/logo.png"),
        },
    ],
}
#     "SITE_URL": "/",
#     "SITE_ICON": {
#         "light": lambda request: static("icon-light.svg"),  # light mode
#         "dark": lambda request: static("icon-dark.svg"),  # dark mode
#     },
#     "SITE_LOGO": {
#         "light": lambda request: static("logo-light.svg"),  # light mode
#         "dark": lambda request: static("logo-dark.svg"),  # dark mode
#     },
#     "SITE_SYMBOL": "speed",  # symbol from icon set
#     "SHOW_HISTORY": True,  # show/hide "History" button, default: True
#     "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
#     "SHOW_BACK_BUTTON": False,  # show/hide "Back" button on changeform in header, default: False
#     "SHOW_UI_WARNINGS": False,  # show/hide warnings in UI, default: False
#     "ENVIRONMENT": "sample_app.environment_callback",  # environment name in header
#     "ENVIRONMENT_TITLE_PREFIX": "sample_app.environment_title_prefix_callback",  # environment name prefix in title tag
#     "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
#     "THEME": "dark",  # Force theme: "dark" or "light". Will disable theme switcher
#     "LOGIN": {
#         "image": lambda request: static("sample/login-bg.jpg"),
#         "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
#         # Inherits from `unfold.forms.AuthenticationForm`
#         "form": "app.forms.CustomLoginForm",
#     },
#     "STYLES": [
#         lambda request: static("css/style.css"),
#     ],
#     "SCRIPTS": [
#         lambda request: static("js/script.js"),
#     ],
#     "BORDER_RADIUS": "6px",
#     "COLORS": {
#         "base": {
#             "50": "oklch(98.5% .002 247.839)",
#             "100": "oklch(96.7% .003 264.542)",
#             "200": "oklch(92.8% .006 264.531)",
#             "300": "oklch(87.2% .01 258.338)",
#             "400": "oklch(70.7% .022 261.325)",
#             "500": "oklch(55.1% .027 264.364)",
#             "600": "oklch(44.6% .03 256.802)",
#             "700": "oklch(37.3% .034 259.733)",
#             "800": "oklch(27.8% .033 256.848)",
#             "900": "oklch(21% .034 264.665)",
#             "950": "oklch(13% .028 261.692)",
#         },
#         "primary": {
#             "50": "oklch(97.7% .014 308.299)",
#             "100": "oklch(94.6% .033 307.174)",
#             "200": "oklch(90.2% .063 306.703)",
#             "300": "oklch(82.7% .119 306.383)",
#             "400": "oklch(71.4% .203 305.504)",
#             "500": "oklch(62.7% .265 303.9)",
#             "600": "oklch(55.8% .288 302.321)",
#             "700": "oklch(49.6% .265 301.924)",
#             "800": "oklch(43.8% .218 303.724)",
#             "900": "oklch(38.1% .176 304.987)",
#             "950": "oklch(29.1% .149 302.717)",
#         },
#         "font": {
#             "subtle-light": "var(--color-base-500)",  # text-base-500
#             "subtle-dark": "var(--color-base-400)",  # text-base-400
#             "default-light": "var(--color-base-600)",  # text-base-600
#             "default-dark": "var(--color-base-300)",  # text-base-300
#             "important-light": "var(--color-base-900)",  # text-base-900
#             "important-dark": "var(--color-base-100)",  # text-base-100
#         },
#     },
#     "EXTENSIONS": {
#         "modeltranslation": {
#             "flags": {
#                 "en": "🇬🇧",
#                 "fr": "🇫🇷",
#                 "nl": "🇧🇪",
#             },
#         },
#     },
#     "SIDEBAR": {
#         "show_search": False,  # Search in applications and models names
#         "command_search": False,  # Replace the sidebar search with the command search
#         "show_all_applications": False,  # Dropdown with all applications and models
#         "navigation": [
#             {
#                 "title": _("Navigation"),
#                 "separator": True,  # Top border
#                 "collapsible": True,  # Collapsible group of links
#                 "items": [
#                     {
#                         "title": _("Dashboard"),
#                         "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
#                         "link": reverse_lazy("admin:index"),
#                         "badge": "sample_app.badge_callback",
#                         "badge_variant": "info",  # info, success, warning, primary, danger
#                         "badge_style": "solid",  # background fill style
#                         "permission": lambda request: request.user.is_superuser,
#                     },
#                     {
#                         "title": _("Users"),
#                         "icon": "people",
#                         "link": reverse_lazy("admin:auth_user_changelist"),
#                     },
#                 ],
#             },
#         ],
#     },
#     "TABS": [
#         {
#             "models": [
#                 "app_label.model_name_in_lowercase",
#             ],
#             "items": [
#                 {
#                     "title": _("Your custom title"),
#                     "link": reverse_lazy("admin:app_label_model_name_changelist"),
#                     "permission": "sample_app.permission_callback",
#                 },
#             ],
#         },
#     ],
# }


# def dashboard_callback(request, context):
#     """
#     Callback to prepare custom variables for index template which is used as dashboard
#     template. It can be overridden in application by creating custom admin/index.html.
#     """
#     context.update(
#         {
#             "sample": "example",  # this will be injected into templates/admin/index.html
#         }
#     )
#     return context


# def environment_callback(request):
#     """
#     Callback has to return a list of two values represeting text value and the color
#     type of the label displayed in top right corner.
#     """
#     return ["Production", "danger"]  # info, danger, warning, success


# def badge_callback(request):
#     return 3


# def permission_callback(request):
#     return request.user.has_perm("sample_app.change_model")
