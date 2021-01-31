from django.shortcuts import render
from django.http import Http404

# from .models import Article
from .events.models import Show, Event


def plain(request):
    ''' Give em our index, without doing much
    '''
    us = Show.objects.all()
    return render(request, 'index.html',
                  {'upcoming_shows': us})


def show(request, show_id):
    ''' show show details page for a given id
    '''
    try:
        s = Show.objects.get(id=show_id)
    except:
        raise Http404("Show does not exist")

    return render(request, 'show.html',
                  {'show':s})

def event(request):
    ''' Show Event details
    '''
    return render(request, 'event_details.html')
