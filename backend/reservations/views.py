import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db import transaction
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from payments import PaymentStatus, RedirectNeeded

from events.forms import ReservationForm, GuestForm
from events.models import Event
from events import services
from reservations.models import Reservation, Guest, ReservationPayment
from shows.models import Show

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

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
                variant = request.POST['payment-method']
                custom_price = None
                if show.base_ticket_price:
                    raw_custom_price = request.POST.get('custom-price')
                    if raw_custom_price:
                        try:
                            custom_price = Decimal(raw_custom_price)
                            base_price = show.base_ticket_price or Decimal(5.0)
                            min_price = show.get_effective_min_price(base_price)
                            max_price = show.get_effective_max_price(base_price)
                            if not (min_price <= custom_price <= max_price):
                                reservation_form.add_error(None, 'Invalid ticket price selected')
                                return render(request, 'reserve.html', {
                                    'show': show,
                                    'reservation_form': reservation_form,
                                    'guest_formset': guest_formset,
                                    'newsletter': newsletter,
                                    'base_price': base_price,
                                })
                        except (ValueError, TypeError):
                            custom_price = None

                with transaction.atomic():
                    reservation = reservation_form.save()

                    for i in range(guest_count):
                        guest = guest_formset[i].save(commit=False)
                        guest.reservation = reservation
                        guest.save()

                    payment = ReservationPayment.from_reservation(
                        reservation, variant=variant, customer_ip_address=_get_ip(request))
                    if custom_price is not None:
                        payment.custom_ticket_price = custom_price
                        payment.total = reservation.ticket_count() * payment.ticket_price
                    payment.save()

                return redirect('/payment/%s' % payment.pk)
    else:
        reservation_form = ReservationForm(show, prefix='res')
        guest_formset = GuestFormSet(prefix='gues')

    base_price = show.base_ticket_price or show.reservation_price or Decimal(15.0)
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
    logger.info(
        'payment_success: payment=%s status=%s reservation=%s',
        payment_id, reservation_payment.status,
        reservation_payment.reservation_id,
    )

    if reservation_payment.reservation and reservation_payment.status not in (PaymentStatus.REJECTED, PaymentStatus.ERROR):
        try:
            services.send_confirmation_mail(reservation_payment.reservation)
            logger.info('confirmation email sent for payment=%s to=%s', payment_id, reservation_payment.reservation.email)
        except Exception as error:
            logger.error(f'Failed to send confirmation email for payment {payment_id}: {error}')
            try:
                reservation = reservation_payment.reservation
                send_mail(
                    subject='ALERT: Failed to send confirmation email',
                    message=(
                        f'Failed to send confirmation email for payment {payment_id}.\n\n'
                        f'Customer: {reservation.first_name} {reservation.last_name}\n'
                        f'Email: {reservation.email}\n'
                        f'Event: {reservation.event}\n\n'
                        f'Error: {error}\n\n'
                        f'Please resend the confirmation manually.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
    else:
        logger.warning(
            'skipping confirmation email for payment=%s: no reservation or bad status=%s',
            payment_id, reservation_payment.status,
        )

    return redirect('/reservation_status/%s' % reservation_payment.id)


def payment_fail(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, 'payment_failure.html', {'payment': reservation_payment})


# ---------------------------------------------------------------------------
# QR Scanner
# ---------------------------------------------------------------------------

@staff_member_required(login_url="/admin/login/")
def qr_scanner(request):
    return render(request, 'qr_scanner.html')


@staff_member_required()
def get_events(request):
    today = timezone.now().date()
    upcoming_events = (
        Event.objects
        .filter(begin__date__gte=today)
        .select_related('show')
        .order_by('begin')
        .values('id', 'begin', 'show__title')
    )
    return JsonResponse([
        {
            'id': event['id'],
            'title': event['show__title'],
            'begin': event['begin'],
            'date': event['begin'].astimezone().strftime('%d.%m.%y'),
        }
        for event in upcoming_events
    ], safe=False)


@staff_member_required()
def check_in(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        all_names = [f"{reservation.first_name} {reservation.last_name}"]
        all_names.extend(str(guest) for guest in reservation.guests.all())
        if reservation.checked_in:
            return JsonResponse({'error': 'Ticket already checked in',
                                 'reservation_number': str(reservation.id),
                                 'guests': all_names}, status=400)
        reservation.checked_in = True
        reservation.save()
        return JsonResponse({'success': True,
                             'reservation_number': str(reservation.id),
                             'guests': all_names,
                             'is_group': True})
    except Reservation.DoesNotExist:
        pass

    try:
        guest = Guest.objects.get(ticket_id=reservation_id)
        if guest.checked_in:
            return JsonResponse({'error': 'Ticket already checked in',
                                 'reservation_number': str(guest.ticket_id),
                                 'guests': [str(guest)]}, status=400)
        guest.checked_in = True
        guest.save()
        return JsonResponse({'success': True,
                             'reservation_number': str(guest.ticket_id),
                             'guests': [str(guest)]})
    except Guest.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
