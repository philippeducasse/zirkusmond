from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    "zirkusmond.de",
    "www.zirkusmond.de",
    "localhost",
    "127.0.0.1",
]

PAYMENT_USES_SSL = True
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://zirkusmond.de")
PAYMENT_HOST = "zirkusmond.de"
