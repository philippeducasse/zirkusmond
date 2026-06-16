import datetime

from django.shortcuts import redirect, render

from newsletter.forms import NewsletterRegistrationForm
from newsletter.services import register_newsletter_email
from rentals.models import RentalObject
from shows.models import Show


def _upcoming_shows():
    upcoming_shows = Show.objects.prefetch_related("events").all()
    upcoming_shows = list(filter(lambda x: x.show_in_preview(), upcoming_shows))
    upcoming_shows = sorted(
        upcoming_shows,
        key=lambda x: (
            datetime.date(2020, 1, 1)
            if not x.future_events()
            else x.future_events()[0].admission.date()
        ),
    )
    return upcoming_shows


def _rental_objects():
    rental_objects = RentalObject.objects.all()
    return rental_objects


def homepage(request):
    upcoming_shows = _upcoming_shows()[:6]
    newsletter_form = NewsletterRegistrationForm()
    return render(
        request,
        "index.html",
        {
            "upcoming_shows": upcoming_shows,
            "show_all_events_link": True,
            "show_home_link": False,
            "newsletter_form": newsletter_form,
        },
    )


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def rentals(request):
    return render(request, "rentals.html", {"rental_objects": _rental_objects()})


def international(request):
    return render(request, "international.html")


def event_list(request):
    return render(
        request,
        "events.html",
        {
            "upcoming_shows": _upcoming_shows(),
            "show_home_link": True,
            "show_all_events_link": False,
        },
    )


def newsletter_registration(request):
    if request.method == "POST":
        form = NewsletterRegistrationForm(request.POST)
        if form.is_valid():
            register_newsletter_email(form.cleaned_data["email"])
            return render(request, "newsletter_registered.html")

    return redirect("/")


def handle404(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(
        request,
        "error_message.html",
        {"error_code": 500, "error_message": "Server Error"},
        status=500,
    )


def permission_denied(request, exception):
    return render(
        request,
        "error_message.html",
        {"error_code": 403, "error_message": "Permission Denied"},
        status=403,
    )


def bad_request(request, exception):
    return render(
        request,
        "error_message.html",
        {"error_code": 400, "error_message": "Bad Request"},
        status=400,
    )


def impressum(request):
    """display impressum"""
    return render(request, "impressum.html")


def datenschutz(request):
    """display datenschutz"""
    return render(request, "datenschutz.html")


def robots(request):
    """display impressum"""
    private_shows = Show.objects.filter(private=True)
    shows = Show.objects.filter(private=False)
    return render(request, "robots.txt", {"private_shows": private_shows, "shows": shows})


def sitemap(request):
    """sitemap.xml"""
    shows = Show.objects.filter(private=False)
    return render(request, "sitemap.xml", {"shows": shows})
