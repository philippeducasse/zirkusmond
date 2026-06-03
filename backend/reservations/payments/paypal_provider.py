import json
import logging
import os

import requests
from django.conf import settings
from payments import PaymentStatus
from payments.paypal import PaypalProvider as BasePaypalProvider

from reservations.models import ReservationPayment

logger = logging.getLogger(__name__)


class PaypalProvider(BasePaypalProvider):
    def process_data(self, payment, request):
        from django.http import HttpResponseBadRequest, HttpResponseForbidden
        from django.shortcuts import redirect
        from payments import PaymentError

        success_url = payment.get_success_url()
        failure_url = payment.get_failure_url()

        if "token" not in request.GET:
            return HttpResponseForbidden("FAILED")

        payer_id = request.GET.get("PayerID")
        if not payer_id:
            if payment.status != PaymentStatus.CONFIRMED:
                payment.change_status(PaymentStatus.REJECTED)
                return redirect(failure_url)
            return redirect(success_url)

        try:
            executed_payment = self.execute_payment(payment, payer_id)
        except PaymentError:
            return redirect(failure_url)
        except KeyError:
            return HttpResponseBadRequest()

        self.set_response_links(payment, executed_payment)
        payment.attrs.payer_info = executed_payment["payer"]["payer_info"]
        if self._capture:
            payment.captured_amount = payment.total
            type(payment).objects.filter(pk=payment.pk).update(captured_amount=payment.captured_amount)
            # Leave status as WAITING — webhook (PAYMENT.CAPTURE.COMPLETED) confirms the payment
        else:
            payment.change_status(PaymentStatus.PREAUTH)

        payment.save()
        logger.info("paypal execute complete payment=%s status=%s awaiting webhook", payment.pk, payment.status)
        return redirect(success_url)


def _get_access_token(endpoint, client_id, secret):
    response = requests.post(
        f"{endpoint}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json"},
        auth=(client_id, secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def verify_webhook_signature(request, endpoint, client_id, secret, webhook_id):
    headers = request.headers
    access_token = _get_access_token(endpoint, client_id, secret)
    response = requests.post(
        f"{endpoint}/v1/notifications/verify-webhook-signature",
        json={
            "auth_algo": headers.get("Paypal-Auth-Algo"),
            "cert_url": headers.get("Paypal-Cert-Url"),
            "transmission_id": headers.get("Paypal-Transmission-Id"),
            "transmission_sig": headers.get("Paypal-Transmission-Sig"),
            "transmission_time": headers.get("Paypal-Transmission-Time"),
            "webhook_id": webhook_id,
            "webhook_event": json.loads(request.body),
        },
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json().get("verification_status") == "SUCCESS"


def _handle_capture_completed(event):
    resource = event.get("resource", {})
    # parent_payment is the PAY-xxx ID stored on the payment; fall back to resource.id for Orders v2
    transaction_id = resource.get("parent_payment") or resource.get("id")
    if not transaction_id:
        logger.warning("paypal PAYMENT.CAPTURE.COMPLETED missing resource.id")
        return
    payment = ReservationPayment.objects.filter(transaction_id=transaction_id).first()
    if not payment:
        logger.warning("paypal PAYMENT.CAPTURE.COMPLETED no payment found for transaction_id=%s", transaction_id)
        return
    if payment.status != PaymentStatus.CONFIRMED:
        payment.change_status(PaymentStatus.CONFIRMED)
        logger.info("paypal webhook confirmed payment transaction_id=%s", transaction_id)


def process_webhook(request):
    paypal_config = settings.PAYMENT_VARIANTS.get("paypal", (None, {}))[1]
    endpoint = paypal_config.get("endpoint", "https://api.paypal.com")
    client_id = paypal_config.get("client_id", "")
    secret = paypal_config.get("secret", "")
    webhook_id = os.environ.get("PAYPAL_WEBHOOK_ID", "")

    if webhook_id:
        if not verify_webhook_signature(request, endpoint, client_id, secret, webhook_id):
            logger.warning("paypal webhook signature verification failed")
            return False, 400

    event = json.loads(request.body)
    event_type = event.get("event_type")
    logger.info("paypal webhook received: event_type=%s", event_type)

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        _handle_capture_completed(event)

    return True, 200
