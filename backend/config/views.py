import datetime

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from newsletter.forms import NewsletterRegistrationForm
from rentals.models import RentalObject
from shows.models import Show
from shows.serializers import ShowCardSerializer


def _upcoming_shows() -> list[Show]:
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


def _rental_objects() -> QuerySet[RentalObject]:
    rental_objects = RentalObject.objects.all()
    return rental_objects


def homepage(request: HttpRequest) -> HttpResponse:
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


@api_view(["GET"])
def homepage_api(request: Request) -> Response:
    shows = _upcoming_shows()[:6]
    return Response({"upcoming_shows": ShowCardSerializer(shows, many=True).data})


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "about.html")


def contact(request: HttpRequest) -> HttpResponse:
    return render(request, "contact.html")


def rentals(request: HttpRequest) -> HttpResponse:
    return render(request, "rentals.html", {"rental_objects": _rental_objects()})


def international(request: HttpRequest) -> HttpResponse:
    return render(request, "international.html")


def event_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "events.html",
        {
            "upcoming_shows": _upcoming_shows(),
            "show_home_link": True,
            "show_all_events_link": False,
        },
    )


def handle404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "error_message.html",
        {"error_code": 500, "error_message": "Server Error"},
        status=500,
    )


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(
        request,
        "error_message.html",
        {"error_code": 403, "error_message": "Permission Denied"},
        status=403,
    )


def bad_request(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(
        request,
        "error_message.html",
        {"error_code": 400, "error_message": "Bad Request"},
        status=400,
    )


def impressum(request: HttpRequest) -> HttpResponse:
    """display impressum"""
    return render(request, "impressum.html")


def datenschutz(request: HttpRequest) -> HttpResponse:
    """display datenschutz"""
    return render(request, "datenschutz.html")


def robots(request: HttpRequest) -> HttpResponse:
    """display impressum"""
    private_shows = Show.objects.filter(private=True)
    shows = Show.objects.filter(private=False)
    return render(request, "robots.txt", {"private_shows": private_shows, "shows": shows})


def sitemap(request: HttpRequest) -> HttpResponse:
    """sitemap.xml"""
    shows = Show.objects.filter(private=False)
    return render(request, "sitemap.xml", {"shows": shows})
