from django.urls import include, path

from reservations.payments import views

urlpatterns = [
    path("<uuid:payment_id>/success", views.payment_success),
    path("<uuid:payment_id>/failure", views.payment_fail),
    path("<uuid:payment_id>", views.payment, name="payment"),
    path("", include("payments.urls")),
]
