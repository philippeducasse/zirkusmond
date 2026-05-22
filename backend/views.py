from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
import datetime

from shows.models import Show
from rentals.models import RentalObject
from newsletter.forms import NewsletterRegistrationForm


def _upcoming_shows():
    us = Show.objects.prefetch_related('events').all()
    us = list(filter(lambda x: x.show_in_preview(), us))
    us = sorted(us, key=lambda x: datetime.date(2020, 1, 1) if not x.future_events() else x.future_events()[0].admission.date())
    return us

def _rental_objects():
    rental_objects = RentalObject.objects.all()
    return rental_objects


def plain(request):
    us = _upcoming_shows()[:6]
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
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, 'error_message.html',
                  {'error_code': 500, 'error_message': "Server Error"}, status=500)


def permission_denied(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 403, 'error_message': "Permission Denied"}, status=403)


def bad_request(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 400, 'error_message': "Bad Request"}, status=400)


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
