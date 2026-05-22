import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.urls import reverse
from payments import PurchasedItem
from payments.models import BasePayment

from .reservation import Reservation


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
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}/payment-failure/%s' % self.pk

    def get_success_url(self):
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}/payment-success/%s' % self.pk

    def get_process_url(self) -> str:
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}' + reverse('process_payment', kwargs={'token': self.token})

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
        self = ReservationPayment(*args, **kwargs)
        self.reservation = reservation
        r = reservation.reservant
        self.billing_first_name = r.firstname
        self.billing_last_name = r.surname
        self.billing_address_1 = r.street if r.street is not None else ""
        self.billing_postcode = r.zipcode if r.zipcode is not None else ""
        self.billing_city = r.town if r.town is not None else ""
        self.billing_email = r.email
        self.description = 'Reservations for %s' % reservation.event
        self.total = self.reservation.ticket_count() * self.ticket_price
        self.currency = 'EUR'
        return self

    @admin.display
    def ticket_count(self):
        return self.reservation.ticket_count()

    @admin.display
    def event(self):
        return f'{self.reservation.event}'