from django.urls import path

from reservations.payments import views

urlpatterns = [
    path("paypal-webhook/", views.paypal_webhook),
    path("<uuid:payment_id>/success", views.payment_success),
    path("<uuid:payment_id>/failure", views.payment_fail),
    path("<uuid:payment_id>", views.payment, name="payment"),
]
