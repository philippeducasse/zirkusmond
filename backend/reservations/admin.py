import logging
from typing import Any

from django import forms
from django.contrib import admin, messages
from django.db.models import Field, QuerySet
from django.http import HttpRequest
from django.utils import timezone
from unfold.admin import ModelAdmin

from events.models import Event
from reservations import emails
from reservations.models import Guest, Reservation
from reservations.payments.models import Payment

logger = logging.getLogger(__name__)


class InlineGuest(admin.StackedInline):
    model = Guest
    extra = 0


class ReservationStatusFilter(admin.SimpleListFilter):
    title = "event status"
    parameter_name = "event_status"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[str, str]]:
        return [
            ("upcoming", "Upcoming"),
            ("past", "Past"),
        ]

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[Reservation]
    ) -> QuerySet[Reservation]:
        now = timezone.now()
        if self.value() == "upcoming":
            return queryset.filter(event__begin__gte=now)
        elif self.value() == "past":
            return queryset.filter(event__begin__lt=now)
        return queryset


class ReservationAdmin(ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "email",
        "event",
        "ticket_count",
        "checked_in",
    ]
    list_filter = [ReservationStatusFilter]
    inlines = (InlineGuest,)
    actions = ["resend_confirmation_mail"]
    search_fields = ["first_name", "last_name", "email"]
    ordering = ["-event__begin"]
    fields = ["event", "first_name", "last_name", "email", "checked_in"]
    list_select_related = ["event"]
    date_hierarchy = "event__begin"

    # Resend confirmation email if event date is changed
    def save_model(
        self, request: HttpRequest, obj: Reservation, form: forms.ModelForm, change: bool
    ) -> None:
        event_changed = change and "event" in form.changed_data
        super().save_model(request, obj, form, change)

        if not event_changed or obj.event is None:
            return

        is_paid = Payment.objects.filter(reservation=obj, status=Payment.Status.COMPLETED).exists()

        if not is_paid:
            return

        try:
            emails.send_confirmation_mail(obj)
        except Exception:
            logger.exception(f"Confirmation mail failed to send for event change on {obj.pk}")
            self.message_user(
                request,
                f"Reservation saved, but the confirmation email to {obj.email} could not be sent.",
                level=messages.ERROR,
            )
        else:
            logger.info(f"Confirmation mail sent for event change on {obj.pk}")
            self.message_user(
                request,
                f"Event changed — confirmation email re-sent to {obj.email}.",
                level=messages.INFO,
            )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Reservation]:
        queryset = super().get_queryset(request)
        is_detail_view = request.resolver_match.url_name.endswith("_change")
        if not request.GET.get("event_status") and not is_detail_view:
            queryset = queryset.filter(event__begin__gte=timezone.now())
        return queryset

    def formfield_for_foreignkey(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> forms.ModelChoiceField | None:
        if db_field.name == "event":
            is_upcoming = (
                not request.GET.get("event_status") or request.GET.get("event_status") == "upcoming"
            )
            if is_upcoming:
                kwargs["queryset"] = Event.objects.filter(begin__gte=timezone.now())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(ordering="last_name")
    def last_name(self, obj: Reservation) -> str:
        return obj.last_name

    @admin.display(ordering="first_name")
    def first_name(self, obj: Reservation) -> str:
        return obj.first_name

    @admin.display(ordering="email")
    def email(self, obj: Reservation) -> str:
        return obj.email

    @admin.display(ordering="checked_in")
    def checked_in(self, obj: Reservation) -> bool:
        return obj.checked_in

    checked_in.boolean = True

    @admin.action(description="Resend Reservation confirmation mail")
    def resend_confirmation_mail(
        self, request: HttpRequest, queryset: QuerySet[Reservation]
    ) -> None:
        for reservation in queryset:
            emails.send_confirmation_mail(reservation)


class GuestAdmin(ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "ticket_id",
        "reservation",
        "checked_in",
    ]
    search_fields = ["first_name", "last_name", "ticket_id"]
    raw_id_fields = ["reservation"]
    ordering = ["-reservation__event__begin"]
    list_select_related = ["reservation__event"]

    @admin.display(ordering="last_name")
    def last_name(self, obj: Guest) -> str:
        return obj.last_name

    @admin.display(ordering="first_name")
    def first_name(self, obj: Guest) -> str:
        return obj.first_name

    @admin.display(ordering="checked_in")
    def checked_in(self, obj: Guest) -> bool:
        return obj.checked_in

    checked_in.boolean = True


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Guest, GuestAdmin)
