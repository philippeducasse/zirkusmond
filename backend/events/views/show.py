from django.http import Http404
from django.shortcuts import render, get_object_or_404

from ..models import Show, Event


def show(request, show_id):
    try:
        s = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        raise Http404("Show does not exist")
    return render(request, 'show.html', {'show': s})


def event(request, event_id):
    e = get_object_or_404(Event, pk=event_id)
    return render(request, 'event.html', {'event': e})
