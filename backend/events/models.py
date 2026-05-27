from django.contrib import admin
from django.db import models
from django.utils import timezone
from shows.models import Show
from events.utils import format_datetime
from .managers import UpcomingEventManager, PastEventManager

class Event(models.Model):
    show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True, related_name="events")
    admission = models.DateTimeField("Admission")
    begin = models.DateTimeField("Show Begins")
    reservation_capacity = models.PositiveIntegerField(default=300)
    open_for_reservation = models.BooleanField(default=True)

    class Meta:
        ordering = ["admission"]
        verbose_name_plural = "all events"

    def __str__(self):
        return format_datetime(self.begin, "%A %d.%m.%y at %H:%M")

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.begin and self.admission and self.begin < self.admission:
            errors["begin"] = "Event cannot start before admission opens."
        if errors:
            raise ValidationError(errors)

    @admin.display
    def time_and_date(self):
        return format_datetime(self.begin, "%d.%m.%y at %H:%M")

    def date_str(self):
        return format_datetime(self.begin, "%d.%m.%y")

    def elaborate_date_str(self):
        return format_datetime(self.begin, "%A %d.%m.%y")

    def admission_time(self):
        return format_datetime(self.admission, "%H:%M")

    def begin_time(self):
        return format_datetime(self.begin, "%H:%M")

    @admin.display
    def reserved_tickets(self):
        if hasattr(self, "annotated_reservation_count"):
            return f"{self.annotated_reservation_count}/{self.reservation_capacity}"
        return f"{self.reservation_count()}/{self.reservation_capacity}"

    @admin.display(boolean=True)
    def reservation_open(self) -> bool:
        if not self.open_for_reservation:
            return False
        if self.reservation_count() > self.reservation_capacity:
            return False
        if timezone.now() > self.begin:
            return False
        return True

    @admin.display
    def reservation_count(self):
        if hasattr(self, "annotated_reservation_count"):
            return self.annotated_reservation_count

        from django.db.models import Count
        from payments import PaymentStatus
        from reservations.payments.models import ReservationPayment

        result = ReservationPayment.objects.filter(
            reservation__event=self, status=PaymentStatus.CONFIRMED
        ).aggregate(
            reservations=Count("reservation", distinct=True),
            guests=Count("reservation__guests", distinct=True),
        )
        return (result["reservations"] or 0) + (result["guests"] or 0)

class UpcomingEvent(Event):
    objects = UpcomingEventManager()

    class Meta:
        proxy = True
        verbose_name = "upcoming event"
        verbose_name_plural = (
            "  Upcoming events"  # leave spaces to have it Event up first in admin panel
        )

class PastEvent(Event):
    objects = PastEventManager()

    class Meta:
        proxy = True
        verbose_name = "past event"
        verbose_name_plural = "past events"
