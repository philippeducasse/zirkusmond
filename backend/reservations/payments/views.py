import logging

import stripe
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import RedirectNeeded
from rest_framework import generics, status
from rest_framework.response import Response

from reservations.models import Payment, Reservation, ReservationPayment
from reservations.payments.serializers import (
    CreatePaymentIntentSerializer,
    PaymentIntentResponseSerializer,
)

logger = logging.getLogger(__name__)


def payment(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    try:
        reservation_payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))


class CreatePaymentIntentView(generics.GenericAPIView):
    serializer_class = CreatePaymentIntentSerializer

    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        custom_ticket_price = serializer.validated_data.get("custom_ticket_price")
        payment_method = serializer.validated_data["payment_method"]

        try:
            payment = Payment.create_for_reservation(reservation, custom_ticket_price, payment_method)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        intent = stripe.PaymentIntent.create(
            amount=int(payment.total * 100),
            currency="eur",
            metadata={"reservation_id": str(reservation.id)},
        )
        payment.stripe_payment_intent_id = intent.id
        payment.save()

        payment._client_secret = intent.client_secret
        response_serializer = PaymentIntentResponseSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
