import uuid

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .services import check_in_ticket, get_upcoming_events


@staff_member_required(login_url="/admin/login/")
def qr_scanner(request: HttpRequest) -> HttpResponse:
    return render(request, "qr_scanner.html")


@staff_member_required()
def get_events(request: HttpRequest) -> JsonResponse:
    events = [
        {
            "id": e["id"],
            "title": e["show__title"],
            "begin": e["begin"],
            "date": e["begin"].astimezone().strftime("%d.%m.%y"),
        }
        for e in get_upcoming_events()
    ]
    return JsonResponse(events, safe=False)


@staff_member_required()
def check_in(request: HttpRequest, reservation_id: uuid.UUID) -> JsonResponse:
    result, status_code = check_in_ticket(reservation_id)
    return JsonResponse(result, status=status_code)
