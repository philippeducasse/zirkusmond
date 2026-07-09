from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from events.models import Event


class UpcomingEventManager(models.Manager):
    def get_queryset(self) -> "QuerySet[Event]":
        return super().get_queryset().filter(begin__gte=timezone.now()).distinct()


class PastEventManager(models.Manager):
    def get_queryset(self) -> "QuerySet[Event]":
        return super().get_queryset().exclude(begin__gte=timezone.now()).distinct()
