from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from .models import Show


class UpcomingShowManager(models.Manager):
    def get_queryset(self) -> QuerySet["Show"]:
        return super().get_queryset().filter(events__begin__gte=timezone.now()).distinct()


class PastShowManager(models.Manager):
    def get_queryset(self) -> QuerySet["Show"]:
        return super().get_queryset().exclude(events__begin__gte=timezone.now()).distinct()


class UnscheduledShowManager(models.Manager):
    def get_queryset(self) -> QuerySet["Show"]:
        return super().get_queryset().filter(events__isnull=True).distinct()
