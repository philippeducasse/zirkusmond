from payments import RedirectNeeded
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
