from django.db import models
from django.utils import timezone


class UpcomingReservationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(event__begin__gte=timezone.now())
            .select_related("event__show")
            .distinct()
        )


class PastReservationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(event__begin__lt=timezone.now())
            .select_related("event__show")
            .distinct()
        )
