import json
import logging
import os
from decimal import ROUND_HALF_UP, Decimal

import requests
from django.conf import settings
from payments import PaymentStatus, RedirectNeeded
from payments.core import BasicProvider

from reservations.models import ReservationPayment

logger = logging.getLogger(__name__)

CENTS = Decimal("0.01")


class PaypalProvider(BasicProvider):
    def __init__(self, client_id, secret, endpoint="https://api.sandbox.paypal.com", capture=True):
        self.client_id = client_id
        self.secret = secret
        self.endpoint = endpoint
        self.orders_url = f"{endpoint}/v2/checkout/orders"
        super().__init__(capture=capture)

    def _auth_headers(self):
        token = _get_access_token(self.endpoint, self.client_id, self.secret)
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    def get_form(self, payment, data=None):
        if not payment.id:
            payment.save()

        extra_data = json.loads(payment.extra_data or "{}")
        approval_url = extra_data.get("approval_url")

        if not approval_url:
            return_url = self.get_return_url(payment)
            total = str(payment.total.quantize(CENTS, rounding=ROUND_HALF_UP))
            response = requests.post(
                self.orders_url,
                json={
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {"currency_code": payment.currency, "value": total},
                        "description": payment.description,
                    }],
                    "payment_source": {
                        "paypal": {
                            "experience_context": {
                                "return_url": return_url,
                                "cancel_url": return_url,
                                "user_action": "PAY_NOW",
                            }
                        }
                    },
                },
                headers=self._auth_headers(),
            )
            response.raise_for_status()
            order = response.json()
            payment.transaction_id = order["id"]
            approval_url = next(link["href"] for link in order["links"] if link["rel"] == "payer-action")
            extra_data["approval_url"] = approval_url
            payment.extra_data = json.dumps(extra_data)

        payment.change_status(PaymentStatus.WAITING)
        raise RedirectNeeded(approval_url)

    def process_data(self, payment, request):
        from django.http import HttpResponseForbidden
        from django.shortcuts import redirect

        success_url = payment.get_success_url()
        failure_url = payment.get_failure_url()

        order_id = request.GET.get("token")
        if not order_id:
            return HttpResponseForbidden("FAILED")

        payer_id = request.GET.get("PayerID")
        if not payer_id:
            if payment.status != PaymentStatus.CONFIRMED:
                payment.change_status(PaymentStatus.REJECTED)
            return redirect(failure_url)

        try:
            response = requests.post(
                f"{self.orders_url}/{order_id}/capture",
                json={},
                headers=self._auth_headers(),
            )
            response.raise_for_status()
            capture = response.json()
        except Exception as e:
            logger.error("paypal v2 capture failed order_id=%s error=%s", order_id, e)
            payment.change_status(PaymentStatus.ERROR)
            return redirect(failure_url)

        capture_status = capture.get("status")
        if capture_status in ("DECLINED", "FAILED", "VOIDED"):
            payment.change_status(PaymentStatus.REJECTED)
            return redirect(failure_url)

        payment.captured_amount = payment.total
        type(payment).objects.filter(pk=payment.pk).update(captured_amount=payment.captured_amount)
        payment.save()
        # Leave WAITING — PAYMENT.CAPTURE.COMPLETED webhook confirms
        logger.info("paypal v2 captured order_id=%s status=%s awaiting webhook", order_id, capture_status)
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
    # v2: order_id in supplementary_data.related_ids; v1 fallback: parent_payment
    transaction_id = (
        resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
        or resource.get("parent_payment")
        or resource.get("id")
    )
    if not transaction_id:
        logger.warning("paypal PAYMENT.CAPTURE.COMPLETED missing transaction id")
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