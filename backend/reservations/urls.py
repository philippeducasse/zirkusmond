from django.urls import include, path

from reservations import views

urlpatterns = [
    path("reserve/<int:show_id>", views.reserve, name="reserve"),
    path("reservation/<int:show_id>", views.reserve_api, name="reserve_api"),
    path("payments/", include("reservations.payments.urls")),
    path("qr-scanner/", include("reservations.qr_scanner.urls")),
]
