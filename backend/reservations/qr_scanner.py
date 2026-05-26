from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render

from reservations import services


@staff_member_required(login_url="/admin/login/")
def qr_scanner(request):
    return render(request, 'qr_scanner.html')


@staff_member_required()
def get_events(request):
    events = [
        {
            'id': e['id'],
            'title': e['show__title'],
            'begin': e['begin'],
            'date': e['begin'].astimezone().strftime('%d.%m.%y'),
        }
        for e in services.get_upcoming_events()
    ]
    return JsonResponse(events, safe=False)


@staff_member_required()
def check_in(request, reservation_id):
    result, status_code = services.check_in_ticket(reservation_id)
    return JsonResponse(result, status=status_code)