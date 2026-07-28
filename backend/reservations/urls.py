from django.urls import include, path

from reservations import views

urlpatterns = [
    path("reservation/<int:show_id>", views.reserve, name="reserve"),
    path(
        "reservation/detail/<uuid:reservation_id>",
        views.reservation_detail,
        name="reservation_detail",
    ),
    path("payments/", include("reservations.payments.urls")),
    path("qr-scanner/", include("reservations.qr_scanner.urls")),
]
