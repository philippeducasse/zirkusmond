import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import RedirectNeeded

from ..models import ReservationPayment
from .. import services

logger = logging.getLogger(__name__)


def payment(request, payment_id, payment_variant=None):
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    if payment_variant:
        payment.variant = payment_variant
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    return TemplateResponse(request, 'payment.html', {'form': form, 'payment': payment})


def payment_success(request, payment_id):
    payment = get_object_or_404(ReservationPayment, id=payment_id)

    if payment.reservation:
        try:
            services.send_confirmation_mail(payment.reservation)
        except Exception as e:
            logger.error(f'Failed to send confirmation email for payment {payment_id}: {e}')
            try:
                reservant = payment.reservation.reservant
                send_mail(
                    subject='ALERT: Failed to send confirmation email',
                    message=(
                        f'Failed to send confirmation email for payment {payment_id}.\n\n'
                        f'Customer: {reservant.firstname} {reservant.surname}\n'
                        f'Email: {reservant.email}\n'
                        f'Event: {payment.reservation.event}\n\n'
                        f'Error: {e}\n\n'
                        f'Please resend the confirmation manually.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

    return redirect('/reservation_status/%s' % payment.id)


def payment_fail(request, payment_id):
    p = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, 'payment_failure.html', {'payment': p})
