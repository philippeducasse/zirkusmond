from io import BytesIO

import xlsxwriter
from django.contrib import admin
from django.db.models import (
    Count,
    DecimalField,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, Lower
from django.http import HttpRequest, HttpResponse
from unfold.admin import ModelAdmin
from unfold.decorators import action
from xlsxwriter.worksheet import Worksheet

from events.models import Event, PastEvent, UpcomingEvent
from reservations.models import Guest, Payment, Reservation
from reservations.payments.admin import reservation_to_dict, send_email_to_reservants


class BaseEventAdmin(ModelAdmin):
    list_display = [
        "show",
        "begin",
        "time_and_date",
        "reservation_open",
        "reserved_tickets",
        "revenue",
    ]
    search_fields = ["show__title"]
    actions = ["print_reservations", "send_to_reservants"]
    actions_detail = ["send_mail_to_reservants_detail"]
    ordering = ["-begin"]
    date_hierarchy = "begin"

    class Media:
        css = {
            "all": ("admin/css/mobile-responsive-admin.css",),
        }

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("show")

        confirmed_reservations = (
            Payment.objects.filter(
                reservation__event=OuterRef("pk"),
                status=Payment.Status.COMPLETED,
            )
            .values("reservation__event")
            .annotate(count=Count("reservation", distinct=True))
            .values("count")
        )

        confirmed_guests = (
            Guest.objects.filter(
                reservation__event=OuterRef("pk"),
                reservation__payment__status=Payment.Status.COMPLETED,
            )
            .values("reservation__event")
            .annotate(count=Count("pk", distinct=True))
            .values("count")
        )

        revenue_subquery = (
            Payment.objects.filter(
                reservation__event=OuterRef("pk"),
                status=Payment.Status.COMPLETED,
            )
            .values("reservation__event")
            .annotate(total=Sum("total"))
            .values("total")
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
            ),
            total_revenue=Subquery(revenue_subquery, output_field=DecimalField()),
        )
        return queryset

    @admin.display(description="Revenue", ordering="total_revenue")
    def revenue(self, obj: Event) -> str:
        if obj.total_revenue is None:
            return "—"
        return f"€ {obj.total_revenue:.2f}"

    @admin.action(description="Print Reservation List")
    def print_reservations(
        self, request: HttpRequest, queryset: QuerySet[Event]
    ) -> HttpResponse | None:
        for event in queryset:
            payments = Payment.objects.filter(
                reservation__event=event, status=Payment.Status.COMPLETED
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

            def add_row(
                worksheet: Worksheet, row: int, person: Reservation | Guest, count: int
            ) -> None:
                worksheet.write_row(
                    row,
                    0,
                    [
                        person.first_name,
                        person.last_name,
                        getattr(person, "email", ""),
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
    def send_to_reservants(self, request: HttpRequest, queryset: QuerySet[Event]) -> HttpResponse:
        all_payments: list[Payment] = []
        for event in queryset:
            all_payments += list(
                Payment.objects.filter(status=Payment.Status.COMPLETED, reservation__event=event)
            )
        dicts = [reservation_to_dict(payment.reservation) for payment in all_payments]
        return send_email_to_reservants(request, dicts, self)

    @action(description="Send mail to Reservants", url_path="send-mail", icon="mail")
    def send_mail_to_reservants_detail(self, request: HttpRequest, object_id: str) -> HttpResponse:
        payments = Payment.objects.filter(
            status=Payment.Status.COMPLETED, reservation__event_id=object_id
        )
        dicts = [reservation_to_dict(p.reservation) for p in payments]
        return send_email_to_reservants(request, dicts, self)


class EventAdmin(BaseEventAdmin):
    list_filter = ["begin"]


class UpcomingEventAdmin(BaseEventAdmin):
    list_filter = ["open_for_reservation"]


class PastEventAdmin(BaseEventAdmin):
    list_filter = []


admin.site.register(Event, EventAdmin)
admin.site.register(UpcomingEvent, UpcomingEventAdmin)
admin.site.register(PastEvent, PastEventAdmin)
