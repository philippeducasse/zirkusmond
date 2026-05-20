import uuid

from django.contrib import admin
from django.db import models

from .event import Event


class Person(models.Model):
    firstname = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)

    street = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.PositiveIntegerField(null=True, blank=True)
    town = models.CharField(max_length=25, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    phonenumber = models.CharField(max_length=25, null=True, blank=True)

    @admin.display
    def event(self):
        reservation = Reservation.objects.filter(
            reservant=self
        ).select_related('event').first()
        if reservation:
            return reservation.event

        try:
            guest = Guest.objects.select_related(
                'event_reservation__event'
            ).get(id=self.id)
            return guest.event_reservation.event
        except Guest.DoesNotExist:
            return None

    def __str__(self):
        return '%s %s' % (self.firstname, self.surname)


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    reservant = models.ForeignKey(Person, on_delete=models.CASCADE)
    checked_in = models.BooleanField(default=False)

    def guests(self):
        return Guest.objects.filter(event_reservation=self)

    @admin.display
    def ticket_count(self):
        return Guest.objects.filter(event_reservation=self).count() + 1

    def __str__(self):
        return 'Reg %s, %s, %s Tickets for %s' % (
            self.reservant.surname, self.reservant.firstname, self.ticket_count(), self.event)


class Guest(Person):
    event_reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    ticket_id = models.UUIDField(unique=True, null=True, default=uuid.uuid4, editable=False)
    checked_in = models.BooleanField(default=False)
