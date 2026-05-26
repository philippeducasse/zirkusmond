import logging
from decimal import Decimal

from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from payments import RedirectNeeded

from events.forms import ReservationForm, GuestForm
from reservations import paypal as paypal_handler
from reservations import services
from reservations.models import ReservationPayment
from shows.models import Show

logger = logging.getLogger(__name__)


def _get_ip(request):
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META else 'REMOTE_ADDR'
    return request.META[key]


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

def reserve(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    GuestFormSet = formset_factory(GuestForm, max_num=9, extra=9)
    newsletter = False

    if request.method == 'POST':
        reservation_form = ReservationForm(show, request.POST, prefix='res')
        guest_formset = GuestFormSet(request.POST, prefix='gues')
        newsletter = request.POST.get('newsletter', False)
        guest_count = 0

        if reservation_form.is_valid():
            guest_count = reservation_form.cleaned_data['attendee_count'] - 1

        if reservation_form.is_valid() and all(guest_formset[i].is_valid() for i in range(guest_count)):
            variant = request.POST['payment-method']
            custom_price = None

            if show.base_ticket_price:
                try:
                    custom_price = services.parse_custom_price(show, request.POST.get('custom-price'))
                except ValueError as e:
                    reservation_form.add_error(None, str(e))
                    base_price = show.base_ticket_price or Decimal(5.0)
                    return render(request, 'reserve.html', {
                        'show': show,
                        'reservation_form': reservation_form,
                        'guest_formset': guest_formset,
                        'newsletter': newsletter,
                        'base_price': base_price,
                    })

            payment = services.create_reservation_with_payment(
                reservation_form, guest_formset, guest_count, variant, custom_price, _get_ip(request)
            )
            return redirect('/payment/%s' % payment.pk)
    else:
        reservation_form = ReservationForm(show, prefix='res')
        guest_formset = GuestFormSet(prefix='gues')

    base_price = show.base_ticket_price or show.reservation_price or Decimal(15.0)
    return render(request, 'reserve.html', {
        'show': show,
        'reservation_form': reservation_form,
        'guest_formset': guest_formset,
        'newsletter': newsletter,
        'base_price': base_price,
        'min_price': show.get_effective_min_price(base_price),
        'max_price': show.get_effective_max_price(base_price),
    })


def reservation_status(request, payment_id):
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, 'reservation_status.html', {
        'payment': payment,
        'show': payment.reservation.event.show,
    })


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

def payment(request, payment_id, payment_variant=None):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    if payment_variant:
        reservation_payment.variant = payment_variant
    try:
        form = reservation_payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    return TemplateResponse(request, 'payment.html', {'form': form, 'payment': reservation_payment})


def payment_success(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    logger.info('payment_success: payment=%s status=%s', payment_id, reservation_payment.status)
    return redirect('/reservation_status/%s' % reservation_payment.id)


def payment_fail(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, 'payment_failure.html', {'payment': reservation_payment})


# ---------------------------------------------------------------------------
# PayPal Webhook
# ---------------------------------------------------------------------------

@csrf_exempt
def paypal_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        _, status_code = paypal_handler.process_webhook(request)
        return HttpResponse(status=status_code)
    except Exception as e:
        logger.error('paypal webhook error: %s', e)
        return HttpResponse(status=500)