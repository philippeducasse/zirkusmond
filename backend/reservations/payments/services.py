from decimal import Decimal

from django.db import transaction

from events.models import Event
from reservations.models import Guest, Reservation, ReservationPayment


def parse_custom_price(show, raw_custom_price):
    """Returns a validated Decimal price or None. Raises ValueError if out of the allowed range."""
    if not raw_custom_price:
        return None
    try:
        price = Decimal(raw_custom_price)
    except Exception:
        return None
    base_price = show.base_ticket_price or Decimal(5.0)
    if not (
        show.get_effective_min_price(base_price)
        <= price
        <= show.get_effective_max_price(base_price)
    ):
        raise ValueError("Invalid ticket price selected")
    return price


def create_reservation_with_payment(
    reservation_form, guest_formset, guest_count, variant, custom_price
):
    with transaction.atomic():
        reservation = reservation_form.save()
        for i in range(guest_count):
            guest = guest_formset[i].save(commit=False)
            guest.reservation = reservation
            guest.save()
        payment = ReservationPayment.from_reservation(
            reservation, variant=variant, custom_ticket_price=custom_price
        )
        payment.save()
    return payment


def create_reservation(event, first_name, last_name, email, guests):
    """Create reservation for Stripe PaymentIntent flow."""
    with transaction.atomic():
        reservation = Reservation.objects.create(
            event=event,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        for guest_data in guests:
            Guest.objects.create(
                reservation=reservation,
                first_name=guest_data.get("first_name", ""),
                last_name=guest_data.get("last_name", ""),
            )
    return reservation
