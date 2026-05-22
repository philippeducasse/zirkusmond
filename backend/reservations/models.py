# Create your models here.
import uuid

from django.contrib import admin
from django.db import models
from events.models import Event


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

    # add information about the person who booked directly in the reservation object
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField()
    checked_in = models.BooleanField(default=False)

    def guests(self):
        return Guest.objects.filter(event_reservation=self)

    @admin.display
    def ticket_count(self):
        return self.guests.count() + 1  # +1 because Reservation is main guest

    def __str__(self):
        return f"Reservation for {self.event} - tickets: {self.ticket_count()} — bought by {self.last_name} {self.first_name} "


class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="guests")
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    ticket_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"Guest: {self.first_name}, {self.last_name}"
