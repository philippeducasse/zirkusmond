from django.http import JsonResponse

from payments import PaymentStatus, RedirectNeeded
from payments.stripe.providers import StripeProviderV3 as BaseStripeProviderV3


class StripeProviderV3(BaseStripeProviderV3):
    def get_form(self, payment, data=None):
        """Override to avoid storing the Session object."""
        import stripe

        stripe.api_key = self.api_key

        items = []
        for item in payment.get_purchased_items():
            items.append(
                {
                    "price_data": {
                        "currency": payment.currency.lower(),
                        "product_data": {"name": item.name},
                        "unit_amount": int(item.price * 100),
                    },
                    "quantity": item.quantity,
                }
            )

        session = stripe.checkout.Session.create(
            line_items=items,
            mode="payment",
            success_url=payment.get_success_url(),
            cancel_url=payment.get_failure_url(),
            customer_email=payment.billing_email,
            client_reference_id=str(payment.token),
        )

        raise RedirectNeeded(session.url)

    def process_data(self, payment, request):
        """Override to handle explicit payment failures (not session expiration)."""
        event = self.return_event_payload(request)
        event_type = event.get("type")

        if event_type in [
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
        ]:
            try:
                session_info = event["data"]["object"]
            except Exception as e:
                from payments import PaymentError

                raise PaymentError(
                    code=400, message="session not present, check Stripe Dashboard"
                ) from e

            if session_info.get("payment_status") == "paid":
                payment.change_status(PaymentStatus.CONFIRMED)

            payment.attrs.session = session_info
            payment.save()
        elif event_type == "checkout.session.expired":
            payment.change_status(PaymentStatus.ERROR)
            try:
                session_info = event["data"]["object"]
            except Exception as e:
                from payments import PaymentError

                raise PaymentError(
                    code=400, message="session not present, check Stripe Dashboard"
                ) from e

            payment.attrs.session = session_info
            payment.save()
        elif event_type in [
            "charge.failed",
            "payment_intent.payment_failed",
            "checkout.session.async_payment_failed",
        ]:
            # Explicit payment failures - send rejection email
            payment.change_status(PaymentStatus.REJECTED)
            try:
                obj = event["data"]["object"]
                payment.attrs.session = obj
                payment.save()
            except Exception as e:
                from payments import PaymentError

                raise PaymentError(code=400, message="object not present in event") from e

        return JsonResponse({"status": "OK"})
