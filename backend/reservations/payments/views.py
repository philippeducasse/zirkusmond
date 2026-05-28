import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from reservations.models import ReservationPayment
from reservations.payments import paypal_provider as paypal_handler

from payments import RedirectNeeded

logger = logging.getLogger(__name__)


def payment(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    try:
        reservation_payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))


def payment_success(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    logger.info("payment_success: payment=%s status=%s", payment_id, reservation_payment.status)
    return TemplateResponse(
        request,
        "reservation_success.html",
        {
            "payment": reservation_payment,
            "show": reservation_payment.reservation.event.show,
        },
    )


def payment_fail(request, payment_id):
    reservation_payment = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, "payment_failure.html", {"payment": reservation_payment})


@csrf_exempt
def paypal_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        _, status_code = paypal_handler.process_webhook(request)
        return HttpResponse(status=status_code)
    except Exception as e:
        logger.error("paypal webhook error: %s", e)
        return HttpResponse(status=500)


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        from payments.urls import static_callback
        return static_callback(request, variant='stripe')
    except Exception as e:
        import json
        from django.core.mail import send_mail
        logger.error("stripe webhook error: %s", e, exc_info=True)

        try:
            body = json.loads(request.body)
            token = body.get('data', {}).get('object', {}).get('client_reference_id')
            if token:
                try:
                    payment = ReservationPayment.objects.get(token=token)
                    reservation = payment.reservation
                    if reservation:
                        send_mail(
                            subject="Payment Processing - Please Wait",
                            message=f"We're processing your payment. If you don't receive a confirmation email within 5 minutes, please contact us. Order ID: {payment.pk}",
                            from_email="noreply@zirkusmond.de",
                            recipient_list=[reservation.email],
                            fail_silently=True,
                        )
                        logger.info("sent webhook error notification to %s for payment %s", reservation.email, payment.pk)
                except ReservationPayment.DoesNotExist:
                    logger.warning("stripe webhook error: payment not found for token %s", token)
        except Exception as notification_error:
            logger.error("failed to send webhook error notification: %s", notification_error)

        return HttpResponse(status=500)
