# this is a custom provider

import stripe
from django.shortcuts import redirect
from payments import PaymentStatus, RedirectNeeded
from payments.core import BasicProvider, get_base_url

# stripeProvider inherits from BasicProvider
class StripeProvider(BasicProvider):
    def __init__(self, secret_key, **kwargs):
        self.secret_key = secret_key
        stripe.api_key = self.secret_key
        self.callback_host = get_base_url()
        super(StripeProvider, self).__init__(**kwargs)


    def create_stripe_session(self, payment, *args, **kwargs):
       
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Zirkusmond reservation',
                        },
                        'unit_amount': int(payment.total * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{get_base_url()}/reservation_status/{payment.id}'
                
            )
            return checkout_session.url
        except stripe.error.StripeError as e:
            payment.change_status(PaymentStatus.REJECTED)
            raise RedirectNeeded(payment.get_failure_url())
    def get_form(self, payment, data=None):
        session_url = self.create_stripe_session(payment)
        raise RedirectNeeded(session_url)
    def process_data(self, payment, request):
        event = self.validate_stripe_event(request)
        if event and event['type'] == 'checkout.session.completed':
            payment.change_status(PaymentStatus.CONFIRMED)
        else:
            payment.change_status(PaymentStatus.REJECTED)
        return redirect(payment.get_success_url())

    def validate_stripe_event(self, request):
        # Implement the logic to validate the Stripe event
        # This typically involves checking the event signature and type
        # Return the event if valid, None otherwise
        pass  # Placeholder for actual implementation
