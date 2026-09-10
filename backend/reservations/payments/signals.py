import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from reservations.payments.models import Payment

logger = logging.getLogger(__name__)


# Post save signals fire after every instance of the payment is saved.
@receiver(post_save, sender=Payment)
def on_payment_status_changed(
    sender: type[Payment], instance: Payment, created: bool, **kwargs: Any
) -> None:
    # Only process if payment has a reservation
    if not instance.reservation:
        logger.error("Payment %s has no reservation", instance.pk)
        return

    reservation = instance.reservation
    payment_id = instance.pk

    # Import tasks here to avoid circular imports
    from reservations.tasks import send_confirmation_email, send_refund_email

    # Send confirmation email when payment is completed
    if instance.status == Payment.Status.COMPLETED:
        send_confirmation_email.delay(str(reservation.id))
        logger.info("Queued confirmation email for payment=%s to=%s", payment_id, reservation.email)

    # Send refund notification email when payment is refunded
    elif instance.status == Payment.Status.REFUNDED:
        send_refund_email.delay(str(reservation.id))
        logger.info("Queued refund email for payment=%s to=%s", payment_id, reservation.email)
