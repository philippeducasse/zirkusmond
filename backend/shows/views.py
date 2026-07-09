from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from shows.serializers import ShowDetailSerializer

from .models import Show


def show(request: HttpRequest, show_id: int) -> HttpResponse:
    try:
        s = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise Http404("Show does not exist")
    return render(request, "show.html", {"show": s})


@api_view(["GET"])
def get_show(request: Request, show_id: int) -> Response:
    show = get_object_or_404(Show, id=show_id)

    return Response({"show": ShowDetailSerializer(show).data})
