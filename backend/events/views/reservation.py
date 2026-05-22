from decimal import Decimal

from django.db import transaction
from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse

from ..forms import ReservationForm, GuestForm
from ..models import ReservationPayment
from shows.models import Show


def _get_ip(request):
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META else 'REMOTE_ADDR'
    return request.META[key]


def reserve(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    newsletter = False
    GuestFormSet = formset_factory(GuestForm, max_num=9, extra=9)

    if request.method == 'POST':
        reservation_form = ReservationForm(show, request.POST, prefix='res')
        guest_formset = GuestFormSet(request.POST, prefix='gues')

        if 'newsletter' in request.POST:
            newsletter = request.POST['newsletter']

        if reservation_form.is_valid():
            guest_count = reservation_form.cleaned_data['attendee_count'] - 1
            guest_forms_valid = all(guest_formset[i].is_valid() for i in range(guest_count))

            if guest_forms_valid:
                with transaction.atomic():
                    reservation = reservation_form.save()

                    for i in range(guest_count):
                        guest = guest_formset[i].save(commit=False)
                        guest.reservation = reservation
                        guest.save()

                variant = request.POST['payment-method']
                payment = ReservationPayment.from_reservation(
                    reservation, variant=variant, customer_ip_address=_get_ip(request))

                if show.ticket_price:
                    custom_price = request.POST.get('custom-price')
                    if custom_price:
                        try:
                            custom_price = Decimal(custom_price)
                            payment.custom_ticket_price = custom_price
                            base_price = show.ticket_price or Decimal(5.0)
                            if not payment.validate_custom_price(base_price):
                                reservation_form.add_error(None, 'Invalid ticket price selected')
                                return render(request, 'reserve.html', {
                                    'show': show,
                                    'reservation_form': reservation_form,
                                    'guest_formset': guest_formset,
                                    'newsletter': newsletter,
                                    'base_price': base_price,
                                })
                            payment.total = reservation.ticket_count() * payment.ticket_price
                        except (ValueError, TypeError):
                            pass

                payment.save()
                return redirect('/payment/%s' % payment.pk)
    else:
        reservation_form = ReservationForm(show, prefix='res')
        guest_formset = GuestFormSet(prefix='gues')

    base_price = show.ticket_price or show.reservation_price or Decimal(15.0)
    min_price = show.get_effective_min_price(base_price)
    max_price = show.get_effective_max_price(base_price)

    return render(request, 'reserve.html', {
        'show': show,
        'reservation_form': reservation_form,
        'guest_formset': guest_formset,
        'newsletter': newsletter,
        'base_price': base_price,
        'min_price': min_price,
        'max_price': max_price,
    })


def reservation_status(request, payment_id):
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    show = payment.reservation.event.show
    return TemplateResponse(request, 'reservation_status.html',
                            {'payment': payment, 'show': show})