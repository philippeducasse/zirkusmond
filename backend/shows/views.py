from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from shows.serializers import ShowDetailSerializer

from .models import Show


@api_view(["GET"])
def get_show(request: Request, show_id: int) -> Response:
    show = get_object_or_404(Show, id=show_id)

    return Response({"show": ShowDetailSerializer(show).data})