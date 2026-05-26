from django.urls import path

from reservations import qr_scanner, views

urlpatterns = [
    path('reserve/<int:show_id>', views.reserve, name='reserve'),
    path('reservation_status/<uuid:payment_id>', views.reservation_status),
    path('payment/<uuid:payment_id>', views.payment, name='payment'),
    path('payment/<uuid:payment_id>/<str:payment_variant>', views.payment),
    path('payment-success/<uuid:payment_id>', views.payment_success),
    path('payment-failure/<uuid:payment_id>', views.payment_fail),

    path('qr-scanner/', qr_scanner.qr_scanner),
    path('qr-scanner/get-events', qr_scanner.get_events),
    path('qr-scanner/<uuid:reservation_id>/check-in', qr_scanner.check_in),

    path('payments/paypal-webhook/', views.paypal_webhook),
]
