import json
import logging
import os

import requests
from django.conf import settings
from payments import PaymentStatus

from reservations.models import ReservationPayment

logger = logging.getLogger(__name__)


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
    transaction_id = event.get("resource", {}).get("id")
    if not transaction_id:
        logger.warning("paypal PAYMENT.CAPTURE.COMPLETED missing resource.id")
        return
    payment = ReservationPayment.objects.filter(transaction_id=transaction_id).first()
    if payment and payment.status != PaymentStatus.CONFIRMED:
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
