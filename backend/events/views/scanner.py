from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from ..models import Event
from reservations.models import Reservation, Guest


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
            'id': event['id'],
            'title': event['show__title'],
            'begin': event['begin'],
            'date': event['begin'].astimezone().strftime('%d.%m.%y'),
        }
        for event in upcoming_events
    ], safe=False)


@staff_member_required()
def check_in(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        all_names = [f"{reservation.first_name} {reservation.last_name}"]
        all_names.extend(str(guest) for guest in reservation.guests.all())
        if reservation.checked_in:
            return JsonResponse({'error': 'Ticket already checked in',
                                 'reservation_number': str(reservation.id),
                                 'guests': all_names}, status=400)
        reservation.checked_in = True
        reservation.save()
        return JsonResponse({'success': True,
                             'reservation_number': str(reservation.id),
                             'guests': all_names,
                             'is_group': True})
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.get(ticket_id=reservation_id)
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