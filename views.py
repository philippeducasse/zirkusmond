from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
# from django import forms
from django.views.generic.edit import CreateView
from django.utils import timezone as tz

from .events.models import Show
from .zm.models import Visitor
from .zm.forms import NewsletterRegistrationForm

def _get_ip(request):
    ''' fetches the user ip
    '''
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META.keys() else 'REMOTE_ADDR'
    return request.META[key]


def _get_referer(request):
    return request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META.keys() else ''


def plain(request):
    ''' Give em our index, without doing much
    '''
    us = Show.objects.filter(private=False)
    us = list(filter(lambda x: x.reservation_open(), us))
    v = Visitor(useragent=request.META['HTTP_USER_AGENT'],
                ip=_get_ip(request),
                referer=_get_referer(request),
                time=tz.now())
    v.save()
    newsletter_form = NewsletterRegistrationForm()
    return render(request, 'index.html',
                  {'upcoming_shows': us,
                   'newsletter_form': newsletter_form})


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
