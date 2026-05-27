from django.urls import path, include

from reservations import views

urlpatterns = [
    path("reserve/<int:show_id>", views.reserve, name="reserve"),
    path("payments/", include("reservations.payments.urls")),
    path("qr-scanner/", include("reservations.qr_scanner.urls")),
]
