import logging
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from payments import PaymentStatus
from payments.signals import status_changed

from events import services
from reservations.models import ReservationPayment

logger = logging.getLogger(__name__)


@receiver(status_changed)
def on_payment_status_changed(
    sender: type[ReservationPayment], instance: ReservationPayment, **kwargs: Any
) -> None:
    reservation = getattr(instance, "reservation", None)
    if not reservation:
        logger.error("failed to send retrieve reservation %s", instance)

        return

    payment_id = instance.pk

    if instance.status == PaymentStatus.CONFIRMED:
        try:
            services.send_confirmation_mail(reservation)
            logger.info(
                "confirmation email sent for payment=%s to=%s", payment_id, reservation.email
            )
        except Exception as error:
            logger.error("failed to send confirmation email for payment=%s: %s", payment_id, error)

    elif instance.status == PaymentStatus.REJECTED:
        try:
            send_mail(
                subject="Payment Failed - Please Try Again",
                message=f"Your payment for {reservation.event.show.title} on {reservation.event.admission.strftime('%Y-%m-%d')} failed.\n\nPlease try again or contact us for assistance.\n\nOrder ID: {payment_id}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.email],
                fail_silently=False,
            )
            logger.info(
                "payment failure email sent for payment=%s to=%s", payment_id, reservation.email
            )
        except Exception as error:
            logger.error(
                "failed to send payment failure email for payment=%s: %s", payment_id, error
            )
