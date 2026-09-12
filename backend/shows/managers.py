from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from .models import PastShow, UnscheduledShow, UpcomingShow


class UpcomingShowManager(models.Manager["UpcomingShow"]):
    def get_queryset(self) -> QuerySet["UpcomingShow"]:
        return super().get_queryset().filter(events__begin__gte=timezone.now()).distinct()


class PastShowManager(models.Manager["PastShow"]):
    def get_queryset(self) -> QuerySet["PastShow"]:
        return super().get_queryset().exclude(events__begin__gte=timezone.now()).distinct()


class UnscheduledShowManager(models.Manager["UnscheduledShow"]):
    def get_queryset(self) -> QuerySet["UnscheduledShow"]:
        return super().get_queryset().filter(events__isnull=True).distinct()
