from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from reservations.models import Reservation, Guest, ReservationPayment


def parse_custom_price(show, raw_custom_price):
    """Returns a validated Decimal price or None. Raises ValueError if out of the allowed range."""
    if not raw_custom_price:
        return None
    try:
        price = Decimal(raw_custom_price)
    except Exception:
        return None
    base_price = show.base_ticket_price or Decimal(5.0)
    if not (show.get_effective_min_price(base_price) <= price <= show.get_effective_max_price(base_price)):
        raise ValueError('Invalid ticket price selected')
    return price


def create_reservation_with_payment(reservation_form, guest_formset, guest_count, variant, custom_price, ip_address):
    with transaction.atomic():
        reservation = reservation_form.save()
        for i in range(guest_count):
            guest = guest_formset[i].save(commit=False)
            guest.reservation = reservation
            guest.save()
        payment = ReservationPayment.from_reservation(reservation, variant=variant, customer_ip_address=ip_address)
        if custom_price is not None:
            payment.custom_ticket_price = custom_price
            payment.total = reservation.ticket_count() * payment.ticket_price
        payment.save()
    return payment


def check_in_ticket(ticket_id):
    """Returns (response_dict, http_status_code)."""
    try:
        reservation = Reservation.objects.get(id=ticket_id)
        names = [f"{reservation.first_name} {reservation.last_name}"]
        names.extend(str(g) for g in reservation.guests.all())
        if reservation.checked_in:
            return {'error': 'Ticket already checked in', 'reservation_number': str(reservation.id), 'guests': names}, 400
        reservation.checked_in = True
        reservation.save()
        return {'success': True, 'reservation_number': str(reservation.id), 'guests': names, 'is_group': True}, 200
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.get(ticket_id=ticket_id)
        if guest.checked_in:
            return {'error': 'Ticket already checked in', 'reservation_number': str(guest.ticket_id), 'guests': [str(guest)]}, 400
        guest.checked_in = True
        guest.save()
        return {'success': True, 'reservation_number': str(guest.ticket_id), 'guests': [str(guest)]}, 200
    except Guest.DoesNotExist:
        return {'error': 'Ticket not found'}, 404


def get_upcoming_events():
    from events.models import Event
    today = timezone.now().date()
    return (
        Event.objects
        .filter(begin__date__gte=today)
        .select_related('show')
        .order_by('begin')
        .values('id', 'begin', 'show__title')
    )