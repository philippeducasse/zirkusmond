from django.db import models
from django.utils import timezone


class UpcomingEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(begin__gte=timezone.now()).distinct()


class PastEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(begin__gte=timezone.now()).distinct()
