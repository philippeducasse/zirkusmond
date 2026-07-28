from django.urls import path

from .views import check_in, get_events

urlpatterns = [
    path("get-events", get_events),
    path("<uuid:reservation_id>/check-in", check_in),
]
