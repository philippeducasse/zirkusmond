from django.shortcuts import get_object_or_404, render

from ..models import Event


def event(request, event_id):
    e = get_object_or_404(Event, pk=event_id)
    return render(request, 'event.html', {'event': e})
