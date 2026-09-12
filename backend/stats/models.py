from django.db import models

from .managers import PageViewManager


class PageView(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    path = models.CharField(max_length=255)
    referer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    entered_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["session_key", "entered_at"])]

    objects = PageViewManager()
