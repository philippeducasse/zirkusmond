import logging
import uuid

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from reservations.models import Payment, Reservation
from reservations.payments.serializers import (
    CreatePaymentIntentSerializer,
    PaymentIntentResponseSerializer,
)

logger = logging.getLogger(__name__)


def set_payment_method_from_charge(payment: Payment, charge) -> None:
    """Extract and set payment method from Stripe charge details."""
    details = charge.payment_method_details
    payment_method_type = details.type
    if payment_method_type == "card":
        wallet = details.card.wallet
        wallet_type = wallet.type if wallet else None
        if wallet_type == "apple_pay":
            payment.payment_method = Payment.PaymentMethod.APPLE
        elif wallet_type == "google_pay":
            payment.payment_method = Payment.PaymentMethod.GOOGLE
        elif wallet_type == "link":
            payment.payment_method = Payment.PaymentMethod.LINK
        else:
            payment.payment_method = Payment.PaymentMethod.CARD
    elif payment_method_type == "paypal":
        payment.payment_method = Payment.PaymentMethod.PAYPAL
    elif payment_method_type == "klarna":
        payment.payment_method = Payment.PaymentMethod.KLARNA
    else:
        payment.payment_method = Payment.PaymentMethod.UNKNOWN


class CreatePaymentIntentView(generics.GenericAPIView):
    serializer_class = CreatePaymentIntentSerializer
    authentication_classes = []

    def post(self, request: Request, reservation_id: uuid.UUID) -> Response:
        stripe.api_key = settings.STRIPE_TOKEN

        reservation = get_object_or_404(Reservation, id=reservation_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        custom_ticket_price = serializer.validated_data.get("custom_ticket_price")

        try:
            payment = Payment.create_for_reservation(reservation, custom_ticket_price)
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


def stripe_return(request: HttpRequest) -> HttpResponseRedirect:
    """Handle Stripe redirect after payment attempt."""
    stripe.api_key = settings.STRIPE_TOKEN

    payment_intent_id = request.GET.get("payment_intent")
    reservation_id = request.GET.get("reservationId")

    if not payment_intent_id or not reservation_id:
        frontend_base = settings.FRONTEND_URL
        return redirect(f"{frontend_base}/payment/failure")

    try:
        # Retrieve the payment intent from Stripe to verify status
        intent = stripe.PaymentIntent.retrieve(
            payment_intent_id, expand=["latest_charge.payment_method_details"]
        )

        # Update payment method on the Payment object
        payment_id = None
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment_id = payment.id
            charge = intent.get("latest_charge")
            if charge:
                set_payment_method_from_charge(payment, charge)
                payment.save()
        except Payment.DoesNotExist:
            logger.warning("stripe_return: payment not found for intent %s", payment_intent_id)

        frontend_base = settings.FRONTEND_URL
        if intent.status == "succeeded":
            return redirect(f"{frontend_base}/payment/success?reservationId={reservation_id}")
        else:
            # Get the show_id from the reservation if possible
            show_id = None
            try:
                reservation = Reservation.objects.select_related("event__show").get(
                    id=reservation_id
                )
                if reservation.event and reservation.event.show:
                    show_id = str(reservation.event.show.id)
                    logger.info(
                        "stripe_return: found show_id=%s for reservation=%s",
                        show_id,
                        reservation_id,
                    )
                else:
                    logger.warning(
                        "stripe_return: reservation %s has no event or show", reservation_id
                    )
            except Reservation.DoesNotExist:
                logger.warning("stripe_return: reservation not found: %s", reservation_id)

            # Build failure URL
            failure_url = f"{frontend_base}/payment/failure"
            params = []
            if show_id:
                logger.info("ADDING SHOW ID")
                params.append(f"eventShowId={show_id}")
            if payment_id:
                params.append(f"paymentId={payment_id}")
            if params:
                failure_url += "?" + "&".join(params)

            return redirect(failure_url)
    except stripe.error.StripeError as e:
        logger.error("stripe_return: error retrieving payment intent: %s", e)
        frontend_base = settings.FRONTEND_URL
        return redirect(f"{frontend_base}/payment/failure")


class StripeWebhookView(APIView):
    """Handle Stripe webhook events for PaymentIntent confirmations."""

    authentication_classes = []

    def post(self, request: Request) -> Response | JsonResponse:
        stripe.api_key = settings.STRIPE_TOKEN

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event: stripe.Event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_HOOK_TOKEN
            )
        except ValueError as e:
            logger.error("stripe_webhook: invalid payload: %s", e)
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            logger.error("stripe_webhook: invalid signature: %s", e)
            return Response({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error("stripe_webhook: unexpected error constructing event: %s", e)
            return Response(
                {"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            if (
                event["type"] == "payment_intent.succeeded"
                # or event["type"] == "checkout.session.completed"
            ):
                intent = event["data"]["object"]
                payment_intent_id = intent["id"]

                try:
                    payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                    payment.status = Payment.Status.COMPLETED

                    # Set payment method from latest charge (if not already set)
                    if not payment.payment_method:
                        latest_charge_id = intent.get("latest_charge")
                        if latest_charge_id:
                            try:
                                charge = stripe.Charge.retrieve(
                                    latest_charge_id, expand=["payment_method_details"]
                                )
                                set_payment_method_from_charge(payment, charge)
                            except stripe.error.StripeError as e:
                                logger.warning(
                                    "webhook: failed to retrieve charge %s: %s", latest_charge_id, e
                                )

                    payment.save()
                    logger.info(
                        "payment_completed: payment=%s intent=%s method=%s",
                        payment.id,
                        payment_intent_id,
                        payment.payment_method,
                    )
                except Payment.DoesNotExist:
                    logger.warning(
                        "payment_intent.succeeded: payment not found for %s", payment_intent_id
                    )
                    return Response(
                        {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
                    )

            elif event["type"] in ("payment_intent.payment_failed", "payment_intent.canceled"):
                intent = event["data"]["object"]
                payment_intent_id = intent["id"]

                try:
                    payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                    payment.status = Payment.Status.FAILED
                    payment.save()
                    logger.info(
                        "payment_failed: payment=%s intent=%s event=%s",
                        payment.id,
                        payment_intent_id,
                        event["type"],
                    )
                except Payment.DoesNotExist:
                    logger.warning("%s: payment not found for %s", event["type"], payment_intent_id)
                    return Response(
                        {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
                    )

            elif event["type"] == "charge.refunded":
                charge = event["data"]["object"]
                payment_intent_id = charge.get("payment_intent")

                try:
                    payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                    payment.status = Payment.Status.REFUNDED
                    payment.save()
                    logger.info(
                        "payment_refunded: payment=%s intent=%s", payment.id, payment_intent_id
                    )
                except Payment.DoesNotExist:
                    logger.warning("charge.refunded: payment not found for %s", payment_intent_id)
                    return Response(
                        {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
                    )

        except Exception as e:
            logger.error(
                "stripe_webhook: error processing event type=%s: %s",
                event.get("type"),
                e,
                exc_info=True,
            )
            return Response(
                {"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return JsonResponse({"status": "ok"})
