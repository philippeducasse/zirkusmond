from django.utils import timezone
from payments import PaymentStatus

from reservations.models import Guest, Reservation


def _payment_rejected(reservation):
    payment = reservation.reservationpayment_set.order_by("-created").first()
    return payment is not None and payment.status == PaymentStatus.REJECTED


def _do_check_in(entity, reservation, ticket_id, names, **extra):
    if _payment_rejected(reservation):
        return {
            "error": "Payment rejected",
            "reservation_number": str(ticket_id),
            "guests": names,
        }, 402
    if entity.checked_in:
        return {
            "error": "Ticket already checked in",
            "reservation_number": str(ticket_id),
            "guests": names,
        }, 400
    entity.checked_in = True
    entity.save()
    return {"success": True, "reservation_number": str(ticket_id), "guests": names, **extra}, 200


def check_in_ticket(ticket_id):
    """Returns (response_dict, http_status_code)."""
    try:
        reservation = Reservation.objects.get(id=ticket_id)
        names = [f"{reservation.first_name} {reservation.last_name}"]
        names.extend(str(g) for g in reservation.guests.all())
        return _do_check_in(reservation, reservation, reservation.id, names, is_group=True)
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.get(ticket_id=ticket_id)
        return _do_check_in(guest, guest.reservation, guest.ticket_id, [str(guest)])
    except Guest.DoesNotExist:
        return {"error": "Ticket not found"}, 404


def get_upcoming_events():
    from events.models import Event

    today = timezone.now().date()
    return (
        Event.objects.filter(begin__date__gte=today)
        .select_related("show")
        .order_by("begin")
        .values("id", "begin", "show__title")
    )
