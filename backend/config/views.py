import datetime

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from shows.models import Show
from shows.serializers import ShowCardSerializer


def _upcoming_shows() -> list[Show]:
    upcoming_shows = Show.objects.prefetch_related("events").all()
    upcoming_shows = list(filter(lambda x: x.show_in_preview(), upcoming_shows))
    upcoming_shows = sorted(
        upcoming_shows,
        key=lambda x: (
            datetime.date(2020, 1, 1)
            if not x.future_events()
            else x.future_events()[0].admission.date()
        ),
    )
    return upcoming_shows


@api_view(["GET"])
def homepage_api(request: Request) -> Response:
    shows = _upcoming_shows()[:6]
    return Response({"upcoming_shows": ShowCardSerializer(shows, many=True).data})