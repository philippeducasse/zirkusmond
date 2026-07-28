import uuid
from typing import Any

from django.db.models import QuerySet
from django.utils import timezone

from reservations.models import Guest, Reservation
from reservations.payments.models import Payment


def _payment_failed(reservation: Reservation) -> bool:
    payment = reservation.payment_set.order_by("-created_at").first()
    return payment is not None and payment.status == Payment.Status.FAILED


def _do_check_in(
    entity: Reservation | Guest,
    reservation: Reservation,
    ticket_id: uuid.UUID | None,
    names: list[str],
    **extra: Any,
) -> tuple[dict[str, Any], int]:
    if _payment_failed(reservation):
        return {
            "error": "Payment failed",
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


def check_in_ticket(ticket_id: uuid.UUID) -> tuple[dict[str, Any], int]:
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


def get_upcoming_events() -> QuerySet[dict[str, Any]]:
    from events.models import Event

    today = timezone.now().date()
    return (
        Event.objects.filter(begin__date__gte=today)
        .select_related("show")
        .order_by("begin")
        .values("id", "begin", "show__title")
    )
