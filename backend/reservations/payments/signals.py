import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from reservations import emails
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

    # Send confirmation email when payment is completed
    if instance.status == Payment.Status.COMPLETED:
        try:
            emails.send_confirmation_mail(reservation)
            logger.info(
                "confirmation email sent for payment=%s to=%s", payment_id, reservation.email
            )
        except Exception as error:
            logger.error("failed to send confirmation email for payment=%s: %s", payment_id, error)

    # Send failure email when payment fails
    elif instance.status == Payment.Status.FAILED:
        try:
            # send_mail(
            #     subject="Payment Failed - Please Try Again",
            #     message=f"Your payment for {reservation.event.show.title} on {reservation.event.admission.strftime('%Y-%m-%d')} failed.\n\nPlease try again or contact us for assistance.\n\nOrder ID: {payment_id}",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[reservation.email],
            #     fail_silently=False,
            # )
            logger.info(
                "payment failure email sent for payment=%s to=%s", payment_id, reservation.email
            )
        except Exception as error:
            logger.error(
                "failed to send payment failure email for payment=%s: %s", payment_id, error
            )

    # Send refund notification email when payment is refunded
    elif instance.status == Payment.Status.REFUNDED:
        try:
            emails.send_refund_mail(reservation)
            logger.info("refund email sent for payment=%s to=%s", payment_id, reservation.email)
        except Exception as error:
            logger.error("failed to send refund email for payment=%s: %s", payment_id, error)
