from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import requests
import json

#from .forms import PaymentForm
from payments import PaymentError, PaymentStatus, RedirectNeeded
from payments.core import BasicProvider, get_credit_card_issuer, get_base_url
from payments.forms import PaymentForm

from django.shortcuts import redirect


class KlarnaForm:
    def __init__(self, payment, inner_html):
        self.payment = payment
        self.variant = 'klarna'
        self.method = 'post'
        self.inner_html = inner_html
    def as_p(self):
        return 'BLALBLALBLABLABL'
    


class KlarnaProvider(BasicProvider):
    '''
    BASE URL for environment +  → https://api.klarna.com/checkout/v3/orders/

        Base URLs - Live (production)
        Europe: https://api.klarna.com/
        North America: https://api-na.klarna.com/
        Oceania: https://api-oc.klarna.com/
        Base URLs - Testing (playground)
        Europe: https://api.playground.klarna.com/
        North America: https://api-na.playground.klarna.com/
        Oceania: https://api-oc.playground.klarna.com/
    '''
    def __init__(self, client_id, key,
                 endpoint='https://api.playground.klarna.com/', **kwargs):
        self.client_id = client_id
        self.key = key
        self.endpoint = endpoint
        self.orders_url = endpoint + 'checkout/v3/orders/'
        self.callback_host = get_base_url()
        super(KlarnaProvider, self).__init__(**kwargs)

    def get_token_from_request(self, *args, **kwargs):
        import pdb
        pdb.set_trace()

    def get_form(self, payment, data=None):
        return KlarnaForm(payment, inner_html=self.post(payment))
        return PaymentForm(data=None)
        #raise RedirectNeeded('/payment/process/%s' % payment.id)
        return self.post(payment)

    def post(self, payment, *args, **kwargs):
        '''
        '''
        pi = list(payment.get_purchased_items())[0]
        example = '''
{{
  "purchase_country": "DE",
  "purchase_currency": "EUR",
  "locale": "en-GB",
  "order_amount": {amount},
  "order_tax_amount": 0,
  "order_lines": [
      {{
          "type": "physical",
          "reference": "{sku}",
          "name": "{name}",
          "quantity": {quantity},
          "quantity_unit": "pcs",
          "unit_price": {unit_price},
          "tax_rate": 0,
          "total_amount": {amount},
          "total_discount_amount": 0,
          "total_tax_amount": 0
      }}
    ],
  "merchant_urls": {{
    "terms": "{terms_url}",
    "checkout": "{return_url}",
    "confirmation": "{return_url}",
    "push": "{return_url}"
  }}
}}'''.format(
        terms_url=self.callback_host + '/reserve/' + str(payment.reservation.event.show.id),
        return_url=self.callback_host + '/payments/process/' + payment.token + '/?order_id={checkout.order.id}',
        amount=int(payment.total)*100,
        quantity=int(pi.quantity),
        unit_price=int(pi.price)*100,
        sku=pi.sku,
        name=pi.name)

        r = requests.post(self.orders_url, auth=(self.client_id, self.key),
                          headers={'content-type': 'application/json'},
                          json=json.loads(example))

        return r.json()['html_snippet']

    def process_data(self, payment, request):
        order_id = request.GET['order_id']
        r = requests.get(self.orders_url + '/' + order_id,
                         auth=(self.client_id, self.key), headers={'content-type': 'application/json'})
        payment.extra_data = str(r.json())
        if r.json()['status'] == 'checkout_complete':
            payment.change_status(PaymentStatus.CONFIRMED)
            return redirect(payment.get_success_url())
        else:
            payment.change_status(PaymentStatus.REJECTED)
            return redirect(payment.get_failure_url())

    #def capture(self, payment, amount=None):
        #payment.change_status(PaymentStatus.CONFIRMED)
        #import pdb
        #pdb.set_trace()

        #return amount

    #def release(self, payment):
        #import pdb
        #pdb.set_trace()
        #return None

    #def refund(self, payment, amount=None):
        #import pdb
        #pdb.set_trace()

        #return amount or 0

    #def process_payment(self, payment, request):
        #import pdb
        #pdb.set_trace() 
