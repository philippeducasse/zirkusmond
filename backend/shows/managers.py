from django.db import models
from django.utils import timezone


class UpcomingShowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(event__begin__gte=timezone.now()).distinct()


class PastShowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(event__begin__gte=timezone.now()).distinct()


class UnscheduledShowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(events__isnull=True).distinct()
