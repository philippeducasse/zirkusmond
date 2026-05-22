import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.urls import reverse
from payments import PurchasedItem
from payments.models import BasePayment

from reservations.models import Reservation


class ReservationPayment(BasePayment):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, null=True, on_delete=models.SET_NULL)
    custom_ticket_price = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Custom price selected by user (sliding scale)")

    @property
    def order(self):
        return self

    def get_metadata(self):
        return {
            "event": str(self.reservation),
            "reservation_id": str(self.id),
        }

    def get_failure_url(self):
        protocol = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{protocol}://{settings.PAYMENT_HOST}/payment-failure/%s' % self.pk

    def get_success_url(self):
        protocol = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{protocol}://{settings.PAYMENT_HOST}/payment-success/%s' % self.pk

    def get_process_url(self) -> str:
        protocol = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{protocol}://{settings.PAYMENT_HOST}' + reverse('process_payment', kwargs={'token': self.token})

    def get_purchased_items(self):
        yield PurchasedItem(
            name=f'{self.reservation.event.show.title} {self.reservation.event}',
            sku=self.reservation.event.pk,
            quantity=self.reservation.ticket_count(),
            price=self.ticket_price,
            currency='EUR')

    @property
    def ticket_price(self):
        if self.custom_ticket_price is not None:
            return self.custom_ticket_price
        show = self.reservation.event.show
        price = show.ticket_price if show.ticket_price else show.reservation_price
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
    def from_reservation(reservation: Reservation, *args, **kwargs):
        payment = ReservationPayment(*args, **kwargs)
        payment.reservation = reservation
        payment.billing_first_name = reservation.first_name
        payment.billing_last_name = reservation.last_name
        payment.billing_address_1 = ""
        payment.billing_postcode = ""
        payment.billing_city = ""
        payment.billing_email = reservation.email
        payment.description = 'Reservations for %s' % reservation.event
        payment.total = reservation.ticket_count() * payment.ticket_price
        payment.currency = 'EUR'
        return payment

    @admin.display
    def ticket_count(self):
        return self.reservation.ticket_count()

    @admin.display
    def event(self):
        return f'{self.reservation.event}'