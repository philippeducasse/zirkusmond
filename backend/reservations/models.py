import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.urls import reverse
from payments import PurchasedItem
from payments.models import BasePayment

from events.models import Event


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, null=True, related_name="reservations"
    )
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField()
    checked_in = models.BooleanField(default=False)

    @admin.display
    def ticket_count(self):
        return self.guests.count() + 1

    def __str__(self):
        return f"Reservation for {self.event} - tickets: {self.ticket_count()} — bought by {self.last_name} {self.first_name}"


class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="guests")
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    ticket_id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, null=True, blank=True
    )
    checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"Guest: {self.first_name}, {self.last_name}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        COMPLETED = "completed"
        FAILED = "failed"
        REFUNDED = "refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, null=True, on_delete=models.SET_NULL)
    stripe_payment_intent_id = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    custom_ticket_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_for_reservation(cls, reservation, custom_ticket_price):
        if custom_ticket_price is None:
            raise ValueError("Custom ticket price must be provided")

        reservation = Reservation.objects.select_related("event__show").get(pk=reservation.pk)
        show = reservation.event.show
        base = show.base_ticket_price
        min_price = show.get_effective_min_price(base)
        max_price = show.get_effective_max_price(base)
        if not (min_price <= custom_ticket_price <= max_price):
            raise ValueError(f"Custom price must be between {min_price} and {max_price}")

        ticket_price = Decimal(str(custom_ticket_price))
        total = reservation.ticket_count() * ticket_price
        return cls.objects.create(
            reservation=reservation, custom_ticket_price=custom_ticket_price, total=total
        )


class ReservationPayment(BasePayment):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, null=True, on_delete=models.SET_NULL)
    custom_ticket_price = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    def get_metadata(self):
        return {
            "event": str(self.reservation),
            "reservation_id": str(self.id),
        }

    def get_failure_url(self):
        protocol = "https" if settings.PAYMENT_USES_SSL else "http"
        return f"{protocol}://{settings.PAYMENT_HOST}/payments/{self.pk}/failure"

    def get_success_url(self):
        protocol = "https" if settings.PAYMENT_USES_SSL else "http"
        return f"{protocol}://{settings.PAYMENT_HOST}/payments/{self.pk}/success"

    def get_process_url(self) -> str:
        protocol = "https" if settings.PAYMENT_USES_SSL else "http"
        return f"{protocol}://{settings.PAYMENT_HOST}" + reverse(
            "process_payment", kwargs={"token": self.token}
        )

    def get_purchased_items(self):
        yield PurchasedItem(
            name=f"{self.reservation.event.show.title} {self.reservation.event}",
            sku=self.reservation.event.pk,
            quantity=self.reservation.ticket_count(),
            price=self.ticket_price,
            currency="EUR",
        )

    @property
    def ticket_price(self):
        if self.custom_ticket_price is not None:
            return Decimal(self.custom_ticket_price)
        show = self.reservation.event.show
        price = show.base_ticket_price if show.base_ticket_price else show.reservation_price
        if not price:
            price = Decimal(15.0)
        return price

    def validate_custom_price(self, base_price):
        if self.custom_ticket_price is None:
            return True
        show = self.reservation.event.show
        min_price = show.get_effective_min_price(base_price)
        max_price = show.get_effective_max_price(base_price)
        return min_price <= self.custom_ticket_price <= max_price

    @staticmethod
    def from_reservation(reservation: Reservation, variant: str, custom_ticket_price=None):
        payment = ReservationPayment(
            reservation=reservation,
            variant=variant,
            billing_email=reservation.email,
            description=f"Reservations for {reservation.event}",
            currency="EUR",
            custom_ticket_price=custom_ticket_price,
        )
        payment.total = reservation.ticket_count() * payment.ticket_price
        return payment

    @admin.display
    def ticket_count(self):
        return self.reservation.ticket_count()

    @admin.display
    def event(self):
        return f"{self.reservation.event}"
