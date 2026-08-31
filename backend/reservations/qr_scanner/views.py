import uuid

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from .services import check_in_ticket, get_upcoming_events


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_events(request: Request) -> Response:
    events = [
        {
            "id": e["id"],
            "title": e["show__title"],
            "begin": e["begin"],
            "date": e["begin"].astimezone().strftime("%d.%m.%y"),
        }
        for e in get_upcoming_events()
    ]
    return Response(events)


@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def check_in(
    request: Request,
    reservation_id: uuid.UUID,
) -> Response:
    raw_event = request.query_params.get("event")
    event_id = int(raw_event) if raw_event and raw_event.isdigit() else None
    result, status_code = check_in_ticket(reservation_id, event_id=event_id)

    return Response(result, status=status_code)
