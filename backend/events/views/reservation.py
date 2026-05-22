from decimal import Decimal

from django.db import transaction
from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse

from ..forms import ReservationForm, PersonForm, GuestForm
from ..models import Reservation, ReservationPayment
from shows.models import Show
from payments import RedirectNeeded


def _get_ip(request):
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META else 'REMOTE_ADDR'
    return request.META[key]


def reserve(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    newsletter = False
    GuestFormSet = formset_factory(GuestForm, max_num=9, extra=9)

    if request.method == 'POST':
        rForm = ReservationForm(show, request.POST, prefix='res')
        pForm = PersonForm(request.POST, prefix='pers')
        dgForms = GuestFormSet(request.POST, prefix='gues')

        if 'newsletter' in request.POST:
            newsletter = request.POST['newsletter']

        if rForm.is_valid() and pForm.is_valid():
            gCount = rForm.cleaned_data['attendee_count'] - 1
            guest_forms_valid = all(dgForms[i].is_valid() for i in range(gCount))

            if guest_forms_valid:
                with transaction.atomic():
                    event = rForm.cleaned_data['event']
                    reservant_person = pForm.save()
                    reservation = Reservation(event=event, reservant=reservant_person)
                    reservation.save()

                    for i in range(gCount):
                        guest = dgForms[i].save(commit=False)
                        guest.event_reservation_id = reservation.pk
                        guest.event_reservation = reservation
                        guest.save()

                variant = request.POST['payment-method']
                rP = ReservationPayment.from_reservation(
                    reservation, variant=variant, customer_ip_address=_get_ip(request))

                if show.ticket_price:
                    custom_price = request.POST.get('custom-price')
                    if custom_price:
                        try:
                            custom_price = Decimal(custom_price)
                            rP.custom_ticket_price = custom_price
                            base_price = show.ticket_price or Decimal(5.0)
                            if not rP.validate_custom_price(base_price):
                                pForm.add_error(None, 'Invalid ticket price selected')
                                return render(request, 'reserve.html', {
                                    'show': show, 'rForm': rForm, 'pForm': pForm,
                                    'gForms': dgForms, 'newsletter': newsletter,
                                    'base_price': base_price,
                                })
                            rP.total = reservation.ticket_count() * rP.ticket_price
                        except (ValueError, TypeError):
                            pass

                rP.save()
                return redirect('/payment/%s' % rP.pk)
    else:
        rForm = ReservationForm(show, prefix='res')
        pForm = PersonForm(prefix='pers')
        dgForms = GuestFormSet(prefix='gues')

    base_price = show.ticket_price or show.reservation_price or Decimal(15.0)
    min_price = show.get_effective_min_price(base_price)
    max_price = show.get_effective_max_price(base_price)

    return render(request, 'reserve.html', {
        'show': show,
        'rForm': rForm,
        'pForm': pForm,
        'gForms': dgForms,
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
