from django.db import models

from .managers import PageViewManager


class PageView(models.Model):
    class DeviceChoices(models.TextChoices):
        MOBILE = "mobile"
        TABLET = "tablet"
        DESKTOP = "desktop"
        BOT = "bot"

    session_key = models.CharField(max_length=40, db_index=True)
    path = models.CharField(max_length=255)
    referer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=10, choices=DeviceChoices)

    entered_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["session_key", "entered_at"])]

    objects = PageViewManager()

    @classmethod
    def detect_device(cls, user_agent: str) -> str:
        if any(
            kw in user_agent
            for kw in (
                "bot",
                "spider",
                "crawl",
                "Googlebot",
                "bingbot",
                "facebookexternalhit",
                "Slurp",
            )
        ):
            return cls.DeviceChoices.BOT
        if any(kw in user_agent for kw in ("iPad", "Tablet")):
            return cls.DeviceChoices.TABLET
        if any(kw in user_agent for kw in ("Mobi", "Android", "iPhone")):
            return cls.DeviceChoices.MOBILE

        return cls.DeviceChoices.DESKTOP
