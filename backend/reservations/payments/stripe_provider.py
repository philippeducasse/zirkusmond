from django.http import JsonResponse
from payments import PaymentError, PaymentStatus, RedirectNeeded
from payments.stripe.providers import StripeProviderV3 as BaseStripeProviderV3


class StripeProviderV3(BaseStripeProviderV3):
    def get_token_from_request(self, payment, request) -> str:
        event = self.return_event_payload(request)._to_dict_recursive()
        event_type = event.get("type", "")

        if event_type == "charge.failed":
            pi_id = event.get("data", {}).get("object", {}).get("payment_intent")
            return self._token_from_payment_intent(pi_id, event_type)

        if event_type == "payment_intent.payment_failed":
            pi_id = event.get("data", {}).get("object", {}).get("id")
            return self._token_from_payment_intent(pi_id, event_type)

        return super().get_token_from_request(payment, request)

    def _token_from_payment_intent(self, pi_id, event_type):
        from payments import get_payment_model

        if not pi_id:
            raise PaymentError(code=400, message=f"no payment_intent in {event_type} event")
        payment_model = get_payment_model()
        try:
            p = payment_model.objects.get(extra_data__contains=pi_id)
            return str(p.token)
        except payment_model.DoesNotExist:
            raise PaymentError(code=400, message=f"no payment found for payment_intent {pi_id}")
        except payment_model.MultipleObjectsReturned:
            raise PaymentError(
                code=400, message=f"multiple payments found for payment_intent {pi_id}"
            )

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
        event = self.return_event_payload(request)._to_dict_recursive()
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
