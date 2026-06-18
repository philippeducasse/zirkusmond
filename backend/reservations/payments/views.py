import logging

import stripe
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import RedirectNeeded
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reservations.models import Payment, Reservation, ReservationPayment

logger = logging.getLogger(__name__)


def payment(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    try:
        reservation_payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))


@api_view(["POST"])
def create_payment_intent(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    custom_ticket_price = request.data.get("custom_ticket_price")

    try:
        payment = Payment.create_for_reservation(reservation, custom_ticket_price)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    intent = stripe.PaymentIntent.create(
        amount=int(payment.total * 100),
        currency="eur",
        metadata={"reservation_id": str(reservation.id)},
    )
    payment.stripe_payment_intent_id = intent.id
    payment.save()

    return Response({"client_secret": intent.client_secret})


def payment_success(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    logger.info("payment_success: payment=%s status=%s", payment_id, reservation_payment.status)
    return TemplateResponse(
        request,
        "reservation_success.html",
        {
            "payment": reservation_payment,
            "show": reservation_payment.reservation.event.show,
        },
    )


def payment_fail(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, "payment_failure.html", {"payment": reservation_payment})
