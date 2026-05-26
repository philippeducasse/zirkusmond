import logging

from django.dispatch import receiver
from payments import PaymentStatus
from payments.signals import status_changed

from events import services

logger = logging.getLogger(__name__)


@receiver(status_changed)
def on_payment_confirmed(sender, instance, **kwargs):
    if instance.status != PaymentStatus.CONFIRMED:
        return
    reservation = getattr(instance, 'reservation', None)
    if not reservation:
        return
    payment_id = instance.pk
    try:
        services.send_confirmation_mail(reservation)
        logger.info('confirmation email sent for payment=%s to=%s', payment_id, reservation.email)
    except Exception as error:
        logger.error('failed to send confirmation email for payment=%s: %s', payment_id, error)