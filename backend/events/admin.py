import imaplib
import time
from io import BytesIO

import xlsxwriter
from django.conf import settings
from django.contrib import admin
from django.core.mail import EmailMessage
from django.db.models import (
    Count,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce, Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Context, Template
from django.utils.html import format_html
from payments import PaymentStatus

from . import services
from .forms import EmailTextForm
from events.models import Event
from reservations.models import Guest, Reservation, ReservationPayment
from stats.models import SiteStats


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    list_display = ("deleted_visitors", "purge_link")

    def purge_link(self, obj):
        url = "/mondmin-purge-old-payments"
        return format_html('<a class="button" href="{}">Purge old payments</a>', url)

    purge_link.short_description = "Actions"


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
            imap = imaplib.IMAP4(settings.EMAIL_HOST)
            imap.starttls()
            imap.login(settings.EMAIL_HOST_USER, settings.MAIL_HOST_CRED)

            for reservation_dict in dicts:
                subject, text = render_mail(mail_subject, mail_text, reservation_dict)
                message = EmailMessage(
                    subject,
                    text,
                    "reservation@zirkusmond.de",
                    [f"{reservation_dict['firstname']} {reservation_dict['surname']} <{reservation_dict['email']}>"],
                )
                imap.append(
                    "Sent",
                    "\\SEEN",
                    imaplib.Time2Internaldate(time.time()),
                    str(message.message()).encode(),
                )
                print(message.send())
                time.sleep(0.5)

            imap.logout()
            admin_instance.message_user(request, f"Mail sent to {len(dicts)} recipients")
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


class ReservationPaymentEventFilter(admin.SimpleListFilter):
    title = "Event"
    parameter_name = "event"

    def lookups(self, request, model_admin):
        return [(event.id, str(event)) for event in Event.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reservation__event=self.value())
        return queryset


class EventAdmin(admin.ModelAdmin):
    list_display = ["show", "begin", "time_and_date", "reservation_open", "reserved_tickets"]
    list_filter = ["show", "begin", "admission"]
    search_fields = ["show__title"]
    actions = ["print_reservations", "send_to_reservants"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("show")

        confirmed_reservations = (
            ReservationPayment.objects.filter(
                reservation__event=OuterRef("pk"),
                status=PaymentStatus.CONFIRMED,
            )
            .values("reservation__event")
            .annotate(count=Count("reservation", distinct=True))
            .values("count")
        )

        confirmed_guests = (
            Guest.objects.filter(
                reservation__event=OuterRef("pk"),
                reservation__reservationpayment__status=PaymentStatus.CONFIRMED,
            )
            .values("reservation__event")
            .annotate(count=Count("pk", distinct=True))
            .values("count")
        )

        queryset = queryset.annotate(
            annotated_reservation_count=Coalesce(
                Subquery(confirmed_reservations, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
            + Coalesce(
                Subquery(confirmed_guests, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
        )
        return queryset

    @admin.action(description="Print Reservation List")
    def print_reservations(self, request, queryset):
        for event in queryset:
            payments = ReservationPayment.objects.filter(
                reservation__event=event, status=PaymentStatus.CONFIRMED
            ).order_by(Lower("reservation__last_name"))
            reservations = [payment.reservation for payment in payments]

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.set_landscape()
            worksheet.set_paper(9)  # A4
            worksheet.set_column(0, 3, 15)

            bold = workbook.add_format({"bold": True, "border": 1})
            border = workbook.add_format({"border": 1})

            columns = ["first_name", "last_name", "email", f"{event.date_str()}"]

            def add_row(worksheet, row, person, count):
                worksheet.write_row(
                    row, 0,
                    [
                        person.first_name,
                        person.last_name,
                        getattr(person, 'email', ''),
                        count,
                    ],
                    border,
                )

            worksheet.write_row(0, 0, columns, bold)
            worksheet.repeat_rows(0)
            row = 1
            for reservation in reservations:
                add_row(worksheet, row, reservation, row)
                worksheet.write(row, 0, reservation.first_name, bold)
                row += 1

                for guest in Guest.objects.filter(reservation=reservation):
                    add_row(worksheet, row, guest, row)
                    row += 1

            workbook.close()
            xlsx_data = output.getvalue()

            filename = event.admission.astimezone().strftime("reservation_list_%Y-%m-%d.xlsx")
            response = HttpResponse(
                headers={"Content-Disposition": f'inline; filename="{filename}"'},
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response.write(xlsx_data)
            return response

    @admin.action(description="Send mail to Reservants")
    def send_to_reservants(self, request, queryset):
        all_payments = []
        for event in queryset:
            all_payments += list(
                ReservationPayment.objects.filter(status="confirmed", reservation__event=event)
            )
        dicts = [reservation_to_dict(payment.reservation) for payment in all_payments]
        return send_email_to_reservants(request, dicts, self)


class InlineGuest(admin.StackedInline):
    model = Guest
    extra = 0


class ReservationPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "reservation",
        "status",
        "ticket_count",
        "event",
    ]
    list_filter = ("status", ReservationPaymentEventFilter)
    search_fields = ["reservation__first_name", "reservation__last_name"]

    actions = ["resend_confirmation_mail", "send_to_reservants"]

    @admin.action(description="Resend confirmation E-Mail")
    def resend_confirmation_mail(self, request, queryset):
        for payment in queryset:
            services.send_confirmation_mail(payment.reservation)

    @admin.action(description="Send mail to Reservants")
    def send_to_reservants(self, request, queryset):
        dicts = [reservation_to_dict(payment.reservation) for payment in queryset]
        return send_email_to_reservants(request, dicts, self)


class ReservationAdmin(admin.ModelAdmin):
    inlines = (InlineGuest,)
    actions = ["resend_confirmation_mail"]
    search_fields = ["first_name", "last_name"]

    @admin.action(description="Resend Reservation confirmation mail")
    def resend_confirmation_mail(self, request, queryset):
        for reservation in queryset:
            services.send_confirmation_mail(reservation)


admin.site.register(Event, EventAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReservationPayment, ReservationPaymentAdmin)
admin.site.register(Guest)