from django.contrib import admin
from django.db import models
from django.utils import timezone

from .show import Show


class Event(models.Model):
    show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True)
    admission = models.DateTimeField('Admission')
    begin = models.DateTimeField('Show Begins')
    reservation_capacity = models.PositiveIntegerField(default=150)
    open_for_reservation = models.BooleanField(default=True)

    class Meta:
        ordering = ['admission']

    def __str__(self):
        return self.begin.astimezone().strftime('%A %d.%m.%y at %H:%M')

    @admin.display
    def time_and_date(self):
        return self.begin.astimezone().strftime('%d.%m.%y at %H:%M')

    def date_str(self):
        return self.begin.astimezone().strftime('%d.%m.%y')

    def elaborate_date_str(self):
        return self.begin.astimezone().strftime('%A %d.%m.%y')

    def admission_time(self):
        return self.admission.astimezone().strftime('%H:%M')

    def begin_time(self):
        return self.begin.astimezone().strftime('%H:%M')

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
        if hasattr(self, 'annotated_reservation_count'):
            return self.annotated_reservation_count

        from django.db.models import Count
        from .payment import ReservationPayment
        result = ReservationPayment.objects.filter(
            reservation__event=self
        ).aggregate(
            reservations=Count('reservation', distinct=True),
            guests=Count('reservation__guest', distinct=True)
        )
        return (result['reservations'] or 0) + (result['guests'] or 0)

    @admin.display
    def reserved_tickets(self):
        return f'{self.reservation_count()}/{self.reservation_capacity}'