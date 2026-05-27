import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from payments import RedirectNeeded

from reservations.payments import paypal as paypal_handler
from reservations.payments.models import ReservationPayment

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
