from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import Context, Template
from events import services
from events.forms import EmailTextForm
from events.models import Event
from events.services import purge_old_payments
from payments import PaymentStatus

from reservations.payments.models import ReservationPayment


def reservation_to_dict(reservation):
    return {
        "show_title": reservation.event.show.title,
        "event_time": reservation.event.time_and_date(),
        "firstname": reservation.first_name,
        "surname": reservation.last_name,
        "email": reservation.email,
    }


def render_mail(subject, body, context):
    context = Context(context)
    rendered_subject = Template(subject).render(context)
    rendered_body = Template(body).render(context)
    return rendered_subject, rendered_body


def send_email_to_reservants(request, dicts, admin_instance):
    if "text_field" in request.POST.keys():
        form = EmailTextForm(request.POST)
    else:
        form = EmailTextForm()
    sample_text, sample_subject = None, ""
    if form.is_valid():
        mail_text = form.data["text_field"]
        mail_subject = form.data["subject"]
        sample_subject, sample_text = render_mail(mail_subject, mail_text, dicts[0])

        if "send" in request.POST.keys():
            for reservation_dict in dicts:
                subject, text = render_mail(mail_subject, mail_text, reservation_dict)
                message = EmailMessage(
                    subject,
                    text,
                    "reservation@zirkusmond.de",
                    [
                        f"{reservation_dict['firstname']} {reservation_dict['surname']} <{reservation_dict['email']}>"
                    ],
                )
                message.send()

            return HttpResponseRedirect(request.get_full_path())

    return render(
        request,
        "admin/send_email.html",
        context={
            "data": dicts,
            "form": form,
            "sample_text": sample_text,
            "sample_subject": sample_subject,
            "action": request.POST["action"],
            "select_across": request.POST["select_across"],
            "index": request.POST["index"],
            "selected_action": request.POST.getlist("_selected_action"),
        },
    )


class PurgeForm(forms.Form):
    confirmed_only = forms.BooleanField(
        required=False, initial=False, label="Only confirmed payments"
    )
    dry_run = forms.BooleanField(required=False, initial=True, label="Dry run (no changes)")


@staff_member_required
def purge_old_payments_view(request):
    if request.method == "POST":
        form = PurgeForm(request.POST)
        if form.is_valid():
            result = purge_old_payments(
                confirmed_only=form.cleaned_data["confirmed_only"],
                dry_run=form.cleaned_data["dry_run"],
            )
            if result["dry_run"]:
                messages.info(
                    request,
                    f"[Dry-run] Found {result['payments_found']} payments before {result['cutoff']:%Y-%m-%d}; "
                    f"visitors to add: {result['visitors_to_add']}.",
                )
            else:
                messages.success(
                    request,
                    f"Deleted {result['deleted_count']} payments; "
                    f"+{result['visitors_to_add']} visitors accumulated. "
                    f"deleted_visitors now {result['final_deleted_visitors']}.",
                )
            return redirect("/mondmin-purge-old-payments")
    else:
        form = PurgeForm()

    context = {
        "form": form,
        "title": "Purge old payments (~6 months)",
        "subtitle": "Deletes old ReservationPayments and updates deleted_visitors.",
    }
    return render(request, "admin_purge_old_payments.html", context)


class ReservationPaymentEventFilter(admin.SimpleListFilter):
    title = "Event"
    parameter_name = "event"

    def lookups(self, request, model_admin):
        return [(event.id, str(event)) for event in Event.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reservation__event=self.value())
        return queryset


class ReservationPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "reservation",
        "status",
        "ticket_count",
        "event",
        "ticket_price",
        "confirmed_total",
    ]
    list_filter = ("status", ReservationPaymentEventFilter)
    search_fields = ["reservation__first_name", "reservation__last_name"]
    readonly_fields = ["reservation"]
    actions = ["resend_confirmation_mail", "send_to_reservants"]

    @admin.display(description="Total")
    def confirmed_total(self, obj):
        if obj.status != PaymentStatus.CONFIRMED:
            return "€ 0.00"
        return f"€ {obj.total:.2f}"

    @admin.action(description="Resend confirmation E-Mail")
    def resend_confirmation_mail(self, request, queryset):
        for payment in queryset:
            services.send_confirmation_mail(payment.reservation)

    @admin.action(description="Send mail to Reservants")
    def send_to_reservants(self, request, queryset):
        dicts = [reservation_to_dict(payment.reservation) for payment in queryset]
        return send_email_to_reservants(request, dicts, self)


admin.site.register(ReservationPayment, ReservationPaymentAdmin)
