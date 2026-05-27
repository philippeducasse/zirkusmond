from django.utils import timezone

from reservations.models import Guest, Reservation


def check_in_ticket(ticket_id):
    """Returns (response_dict, http_status_code)."""
    try:
        reservation = Reservation.objects.get(id=ticket_id)
        names = [f"{reservation.first_name} {reservation.last_name}"]
        names.extend(str(g) for g in reservation.guests.all())
        if reservation.checked_in:
            return {
                "error": "Ticket already checked in",
                "reservation_number": str(reservation.id),
                "guests": names,
            }, 400
        reservation.checked_in = True
        reservation.save()
        return {
            "success": True,
            "reservation_number": str(reservation.id),
            "guests": names,
            "is_group": True,
        }, 200
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.get(ticket_id=ticket_id)
        if guest.checked_in:
            return {
                "error": "Ticket already checked in",
                "reservation_number": str(guest.ticket_id),
                "guests": [str(guest)],
            }, 400
        guest.checked_in = True
        guest.save()
        return {
            "success": True,
            "reservation_number": str(guest.ticket_id),
            "guests": [str(guest)],
        }, 200
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
