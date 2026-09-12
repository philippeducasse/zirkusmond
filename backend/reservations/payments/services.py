from decimal import Decimal
from typing import Any

from django.db import transaction

from events.models import Event
from reservations.models import Guest, Reservation
from shows.models import Show


def parse_custom_price(show: Show, raw_custom_price: str | None) -> Decimal | None:
    """Returns a validated Decimal price or None. Raises ValueError if out of the allowed range."""
    if not raw_custom_price:
        return None
    try:
        price = Decimal(raw_custom_price)
    except Exception:
        return None
    base_price = show.base_ticket_price
    if not (
        show.get_effective_min_price(base_price)
        <= price
        <= show.get_effective_max_price(base_price)
    ):
        raise ValueError("Invalid ticket price selected")
    return price


def create_reservation(
    event: Event,
    first_name: str,
    last_name: str,
    email: str,
    guests: list[dict[str, Any]],
) -> Reservation:
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
