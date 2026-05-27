from django.urls import path
from reservations.payments.admin import purge_old_payments_view

app_name = "events_admin"
urlpatterns = [
    path("purge-old-payments/", purge_old_payments_view, name="purge-old-payments"),
]
