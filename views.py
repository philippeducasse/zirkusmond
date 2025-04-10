from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
# from django import forms
from django.views.generic.edit import CreateView
from django.utils import timezone as tz
import datetime

from .events.models import Show
from .zm.models import Visitor, RentalObject
from .zm.forms import NewsletterRegistrationForm

def _get_ip(request):
    ''' fetches the user ip
    '''
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META.keys() else 'REMOTE_ADDR'
    return request.META[key]


def _get_referer(request):
    return request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META.keys() else ''


def _upcoming_shows():
    us = Show.objects.all()
    us = list(filter(lambda x: x.show_in_preview(), us))
    us = sorted(us, key=lambda x: datetime.date(2020, 1, 1) if len(x.events()) == 0 else x.events()[0].admission.date())
    return us

def _rental_objects():
    rental_objects = RentalObject.objects.all()
    return rental_objects


def plain(request):
    ''' Give em our index, without doing much
    '''
    us = _upcoming_shows()[:6]
    ps = Show.objects.filter(private=False)
    # get the last three shows which last date is in the past
    #ps = filter(lambda x: x.last_event() != None, ps)
    #ps = list(filter(lambda x: x.last_event().admission < tz.now(), ps))[-3:]
    # ps = list(filter(lambda x:
    v = Visitor(useragent=request.META['HTTP_USER_AGENT'],
                ip=_get_ip(request),
                referer=_get_referer(request),
                time=tz.now())
    v.save()
    newsletter_form = NewsletterRegistrationForm()
    return render(request, 'index.html',
                  {'upcoming_shows': us,
                   'show_all_events_link': True,
                   'show_home_link': False,
                   'newsletter_form': newsletter_form})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def rentals(request):
    return render(request, 'rentals.html',  {'rental_objects': _rental_objects()})

def international(request):
    return render(request, 'international.html')

def event_list(request):
    return render(request, 'events.html', {'upcoming_shows': _upcoming_shows(), 'show_home_link': True, 'show_all_events_link': False})


def newsletter_registration(request):
    if request.method == 'POST':
        n = NewsletterRegistrationForm(request.POST)
        if n.is_valid():
            n.save()
            return render(request, 'newsletter_registered.html')

    return redirect('/')

def handle404(request, exception):
    '''
    '''
    return render(request, '404.html')


def server_error(request):
    return render(request, 'error_message.html',
                  {'error_code': 500,
                   'error_message': "Server Error"})


def permission_denied(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 403,
                   'error_message': "Permission Denied"})


def bad_request(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 400,
                   'error_message': "Bad Request"})


def impressum(request):
    ''' display impressum
    '''
    return render(request, 'impressum.html')

def datenschutz(request):
    ''' display datenschutz
    '''
    return render(request, 'datenschutz.html')

def robots(request):
    ''' display impressum
    '''
    private_shows = Show.objects.filter(private=True)
    shows = Show.objects.filter(private=False)
    return render(request, 'robots.txt', {'private_shows': private_shows})


def sitemap(request):
    ''' sitemap.xml
    '''
    shows = Show.objects.filter(private=False)
    return render(request, 'sitemap.xml',
                  {'shows': shows})
