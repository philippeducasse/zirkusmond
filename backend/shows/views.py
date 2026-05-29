from django.http import Http404
from django.shortcuts import render

from .models import Show


def show(request, show_id):
    try:
        s = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise Http404("Show does not exist")
    return render(request, "show.html", {"show": s})
