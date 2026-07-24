import logging
import uuid

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import RedirectNeeded
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reservations.models import Payment, Reservation, ReservationPayment
from reservations.payments.serializers import (
    CreatePaymentIntentSerializer,
    PaymentIntentResponseSerializer,
)

logger = logging.getLogger(__name__)


def payment(request: HttpRequest, payment_id: uuid.UUID) -> HttpResponseRedirect | None:
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    try:
        reservation_payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))


class CreatePaymentIntentView(generics.GenericAPIView):
    serializer_class = CreatePaymentIntentSerializer
    authentication_classes = []

    def post(self, request: Request, reservation_id: uuid.UUID) -> Response:
        stripe.api_key = settings.STRIPE_TOKEN

        reservation = get_object_or_404(Reservation, id=reservation_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        custom_ticket_price = serializer.validated_data.get("custom_ticket_price")
        payment_method = serializer.validated_data["payment_method"]

        try:
            payment = Payment.create_for_reservation(reservation, custom_ticket_price, payment_method)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        intent: stripe.PaymentIntent = stripe.PaymentIntent.create(
            amount=int(payment.total * 100),
            currency="eur",
            metadata={"reservation_id": str(reservation.id)},
        )
        payment.stripe_payment_intent_id = intent.id
        payment.save()

        payment._client_secret = intent.client_secret
        response_serializer = PaymentIntentResponseSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


def payment_success(request: HttpRequest, payment_id: uuid.UUID) -> TemplateResponse:
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


def payment_fail(request: HttpRequest, payment_id: uuid.UUID) -> TemplateResponse:
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, "payment_failure.html", {"payment": reservation_payment})


class StripeWebhookView(APIView):
    """Handle Stripe webhook events for PaymentIntent confirmations."""

    authentication_classes = []

    def post(self, request: Request) -> Response | JsonResponse:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event: stripe.Event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_HOOK_TOKEN
            )
        except ValueError:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            payment_intent_id = intent["id"]

            try:
                payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                payment.status = Payment.Status.COMPLETED
                payment.save()
                logger.info(
                    "payment_completed: payment=%s intent=%s", payment.id, payment_intent_id
                )
            except Payment.DoesNotExist:
                logger.warning("payment_intent.succeeded: payment not found for %s", payment_intent_id)
                return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({"status": "ok"})
