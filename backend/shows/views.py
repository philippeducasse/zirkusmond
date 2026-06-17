from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from shows.serializers import ShowDetailSerializer

from .models import Show


def show(request, show_id):
    try:
        s = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise Http404("Show does not exist")
    return render(request, "show.html", {"show": s})


@api_view(["GET"])
def get_show(request, show_id):
    show = get_object_or_404(Show, id=show_id)

    return Response({"show": ShowDetailSerializer(show).data})
