from decimal import Decimal

from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from events.forms import GuestForm, ReservationForm
from events.models import Event
from newsletter.services import register_newsletter_email
from reservations.payments.services import (
    create_reservation_with_payment,
    create_reservation_with_payment_api,
    parse_custom_price,
)
from reservations.serializers import ReservationSerializer
from shows.models import Show


def reserve(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    guest_form_set = formset_factory(GuestForm, max_num=9, extra=9)
    newsletter = False

    if request.method == "POST":
        reservation_form = ReservationForm(show, request.POST, prefix="res")
        guest_formset = guest_form_set(request.POST, prefix="gues")
        newsletter = request.POST.get("newsletter", False)
        guest_count = 0

        if reservation_form.is_valid():
            guest_count = reservation_form.cleaned_data["attendee_count"] - 1

        if reservation_form.is_valid() and all(
            guest_formset[i].is_valid() for i in range(guest_count)
        ):
            variant = request.POST["payment-method"]
            custom_price = None

            if show.base_ticket_price:
                try:
                    custom_price = parse_custom_price(show, request.POST.get("custom-price"))
                except ValueError as e:
                    reservation_form.add_error(None, str(e))
                    base_price = show.base_ticket_price or Decimal(5.0)
                    return render(
                        request,
                        "reserve.html",
                        {
                            "show": show,
                            "reservation_form": reservation_form,
                            "guest_formset": guest_formset,
                            "newsletter": newsletter,
                            "base_price": base_price,
                        },
                    )
            if newsletter:
                register_newsletter_email(reservation_form.cleaned_data["email"])

            payment = create_reservation_with_payment(
                reservation_form,
                guest_formset,
                guest_count,
                variant,
                custom_price,
            )
            return redirect(f"/payments/{payment.pk}")
    else:
        reservation_form = ReservationForm(show, prefix="res")
        guest_formset = guest_form_set(prefix="gues")

    base_price = show.base_ticket_price or show.reservation_price or Decimal(15.0)
    return render(
        request,
        "reserve.html",
        {
            "show": show,
            "reservation_form": reservation_form,
            "guest_formset": guest_formset,
            "newsletter": newsletter,
            "base_price": base_price,
            "min_price": show.get_effective_min_price(base_price),
            "max_price": show.get_effective_max_price(base_price),
        },
    )


@api_view(["POST"])
def reserve_api(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    serializer = ReservationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    event = get_object_or_404(Event, pk=serializer.validated_data["event_id"], show=show)
    if not event.reservation_open():
        return Response(
            {"error": "Reservations are not open for this event"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    custom_price = None
    if show.base_ticket_price:
        try:
            custom_price = parse_custom_price(show, serializer.validated_data.get("custom_price"))
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    payment = create_reservation_with_payment_api(
        event=event,
        first_name=serializer.validated_data["first_name"],
        last_name=serializer.validated_data["last_name"],
        email=serializer.validated_data["email"],
        guests=serializer.validated_data.get("guests", []),
        variant=serializer.validated_data["payment_method"],
        custom_price=custom_price,
    )

    if serializer.validated_data.get("newsletter"):
        register_newsletter_email(serializer.validated_data["email"])

    return Response(
        {"payment_id": payment.pk, "redirect_url": f"/payments/{payment.pk}"},
        status=status.HTTP_201_CREATED,
    )
