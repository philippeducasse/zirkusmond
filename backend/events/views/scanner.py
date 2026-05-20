from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from ..models import Event, Reservation, Guest


@staff_member_required(login_url="/admin/login/")
def qr_scanner(request):
    return render(request, 'qr_scanner.html')


@staff_member_required()
def get_events(request):
    today = timezone.now().date()
    upcoming_events = (
        Event.objects
        .filter(begin__date__gte=today)
        .select_related('show')
        .order_by('begin')
        .values('id', 'begin', 'show__title')
    )
    return JsonResponse([
        {
            'id': e['id'],
            'title': e['show__title'],
            'begin': e['begin'],
            'date': e['begin'].astimezone().strftime('%d.%m.%y'),
        }
        for e in upcoming_events
    ], safe=False)


@staff_member_required()
def check_in(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        total_guests = [str(reservation.reservant)]
        total_guests.extend(str(g) for g in reservation.guests())
        if reservation.checked_in:
            return JsonResponse({'error': 'Ticket already checked in',
                                 'reservation_number': str(reservation.id),
                                 'guests': total_guests}, status=400)
        reservation.checked_in = True
        reservation.save()
        return JsonResponse({'success': True,
                             'reservation_number': str(reservation.id),
                             'guests': total_guests,
                             'is_group': True})
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.select_related('event_reservation__reservant').get(
            ticket_id=reservation_id)
        if guest.checked_in:
            return JsonResponse({'error': 'Ticket already checked in',
                                 'reservation_number': str(guest.ticket_id),
                                 'guests': [str(guest)]}, status=400)
        guest.checked_in = True
        guest.save()
        return JsonResponse({'success': True,
                             'reservation_number': str(guest.ticket_id),
                             'guests': [str(guest)]})
    except Guest.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
