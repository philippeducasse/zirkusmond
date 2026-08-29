from django.urls import include, path

from reservations.payments import views

urlpatterns = [
    path("webhook/stripe", views.StripeWebhookView.as_view(), name="stripe_webhook"),
    path("return/stripe", views.stripe_return, name="stripe_return"),
    path(
        "<uuid:reservation_id>/intent",
        views.CreatePaymentIntentView.as_view(),
        name="create_payment_intent",
    ),
    # django-payments webhook/callback routes (process/<uuid:token>/) — JSON, not HTML templates.
    path("", include("payments.urls")),
]
