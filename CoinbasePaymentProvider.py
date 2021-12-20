from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import requests
import json

import logging
logger = logging.getLogger(__name__)

#from .forms import PaymentForm
from payments import PaymentError, PaymentStatus, RedirectNeeded
from payments.core import BasicProvider, get_credit_card_issuer, get_base_url
from payments.forms import PaymentForm

from django.shortcuts import redirect


class CoinbaseProvider(BasicProvider):
    '''
    '''

    def __init__(self, key, **kwargs):
        self.key = key
        self.base_url = 'https://api.commerce.coinbase.com'
        self.charge_url = self.base_url + '/charges'
        # to be sent with every request
        self.header_base = {'X-CC-Api-Key': self.key,
                            'X-CC-Version': '2018-03-22'}
        super(CoinbaseProvider, self).__init__(**kwargs)

    def create_charge(self, payment):
        purchased_item = list(payment.get_purchased_items())[0]
        charge = {
            "name": purchased_item.name,
            "description": f"{purchased_item.quantity} Tickets for {purchased_item.name}",
            "local_price": {
                "amount": f'{payment.total}',
                "currency": "EUR"
            },
            "pricing_type": "fixed_price",
            "metadata": {
                "customer_name": f'{payment.billing_first_name} {payment.billing_last_name}',
            },
            "redirect_url": f'{get_base_url()}/payments/process/{payment.token}',
            "cancel_url": payment.get_failure_url(),
            }
        r = requests.post(self.charge_url, headers=self.header_base,
                          json=charge)
        return r


    def get_form(self, payment, data=None):
        charge = self.create_charge(payment)
        raise RedirectNeeded(charge.json()['data']['hosted_url'])

    def process_data(self, payment, request):
        j = json.loads(request.body)
        if j['event']['type'] == 'charge:confirmed':
            payment.change_status(PaymentStatus.CONFIRMED)
            logger.error('Charge confirmed')
            return redirect(payment.get_success_url())
        else:
            payment.change_status(PaymentStatus.REJECTED)
            logger.error('Charge denied')
            return redirect(payment.get_failure_url())
