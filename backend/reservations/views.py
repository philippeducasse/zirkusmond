from decimal import Decimal

from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render

from events.forms import GuestForm, ReservationForm
from reservations.payments import services
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
                    custom_price = services.parse_custom_price(
                        show, request.POST.get("custom-price")
                    )
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

            payment = services.create_reservation_with_payment(
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
