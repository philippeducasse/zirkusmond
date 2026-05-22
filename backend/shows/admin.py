from datetime import datetime, timedelta
from datetime import time as dtime

from django import forms
from django.contrib import admin
from django.db.models import (
    Count,
    F,
    IntegerField,
    Min,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from events.models import (
    Event,
    Guest,
    ReservationPayment,
)
from payments import PaymentStatus

from .models import Show


class EventInlineForm(forms.ModelForm):
    event_date = forms.DateField(
        label="Event date",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "event-date-input"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
        required=True,
    )
    show_time = forms.TimeField(
        label="Show time",
        widget=forms.TimeInput(
            attrs={"type": "time", "class": "event-time-input"},
            format="%H:%M",
        ),
        input_formats=["%H:%M"],
        required=True,
    )
    admission_time = forms.TimeField(
        label="Admission time",
        widget=forms.TimeInput(
            attrs={"type": "time", "class": "admission-time-input"},
            format="%H:%M",
        ),
        input_formats=["%H:%M"],
        required=False,
        help_text="Defaults to one hour before the show.",
    )

    class Meta:
        model = Event
        fields = (
            "event_date",
            "show_time",
            "admission_time",
            "reservation_capacity",
            "open_for_reservation",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.begin:
            local_begin = timezone.localtime(self.instance.begin)
            self.fields["event_date"].initial = local_begin.date()
            self.fields["show_time"].initial = local_begin.time().replace(second=0, microsecond=0)
            if self.instance.admission:
                local_admission = timezone.localtime(self.instance.admission)
                self.fields["admission_time"].initial = local_admission.time().replace(
                    second=0, microsecond=0
                )
        else:
            today = timezone.localdate()
            default_time = self._default_show_time_for_date(today)
            self.fields["event_date"].initial = today
            self.fields["show_time"].initial = default_time
            self.fields["admission_time"].initial = (
                datetime.combine(today, default_time) - timedelta(hours=1)
            ).time()

    def _default_show_time_for_date(self, date_value):
        if date_value.weekday() in (4, 5):  # Friday or Saturday
            return dtime(hour=20, minute=0)
        return dtime(hour=19, minute=0)

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get("event_date")
        show_time = cleaned_data.get("show_time")
        if not event_date:
            raise forms.ValidationError("Please provide a date for the event.")
        if not show_time:
            show_time = self._default_show_time_for_date(event_date)

        combined = datetime.combine(event_date, show_time)
        begin_dt = timezone.make_aware(combined, timezone.get_current_timezone())
        cleaned_data["begin"] = begin_dt

        admission = cleaned_data.get("admission")
        admission_time = cleaned_data.get("admission_time")
        if admission_time:
            admission = timezone.make_aware(
                datetime.combine(event_date, admission_time), timezone.get_current_timezone()
            )
        elif admission is None:
            admission = begin_dt - timedelta(hours=1)

        cleaned_data["admission"] = admission
        cleaned_data["computed_begin"] = begin_dt
        cleaned_data["computed_admission"] = admission
        return cleaned_data

    def has_changed(self):
        # For new instances, consider the form changed if event_date has a value
        if not self.instance.pk and self.data:
            prefix = self.prefix
            event_date_key = f"{prefix}-event_date" if prefix else "event_date"
            if self.data.get(event_date_key):
                return True
        return super().has_changed()

    def save(self, commit=True):
        instance = super().save(commit=False)
        begin_dt = self.cleaned_data.get("computed_begin") or self.cleaned_data.get("begin")
        admission_dt = self.cleaned_data.get("computed_admission") or self.cleaned_data.get(
            "admission"
        )

        if begin_dt:
            instance.begin = begin_dt
        if admission_dt:
            instance.admission = admission_dt

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class EventInline(admin.TabularInline):
    model = Event
    form = EventInlineForm
    fields = (
        "event_date",
        "show_time",
        "admission_time",
        "reservation_capacity",
        "open_for_reservation",
    )
    extra = 0
    show_change_link = True

    class Media:
        js = ("events/js/event_inline.js",)


class ShowAdmin(admin.ModelAdmin):
    list_display = ["title", "next_event_date", "dates_text", "reservation_open", "show_in_preview"]
    list_filter = ["private", "last_modified"]
    search_fields = ["title", "description", "cast"]
    ordering = []
    default_ordering = [F("next_event_begin").desc(nulls_last=True), "-title"]
    inlines = [EventInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        events_for_show = Event.objects.filter(show=OuterRef("pk"))
        capacity_subquery = events_for_show.annotate(
            total_capacity=Sum("reservation_capacity")
        ).values("total_capacity")[:1]

        all_payments = ReservationPayment.objects.filter(
            reservation__event__show=OuterRef("pk"),
            status=PaymentStatus.CONFIRMED,
        )
        all_reservations_subquery = (
            all_payments.values("reservation__event__show")
            .annotate(total_reservations=Count("reservation", distinct=True))
            .values("total_reservations")[:1]
        )

        all_guests_qs = Guest.objects.filter(
            event_reservation__event__show=OuterRef("pk"),
            event_reservation__reservationpayment__status=PaymentStatus.CONFIRMED,
        )
        all_guests_subquery = (
            all_guests_qs.values("event_reservation__event__show")
            .annotate(total_guests=Count("pk", distinct=True))
            .values("total_guests")[:1]
        )

        # Prefetch events with their reservation counts pre-calculated
        # This prevents N+1 queries when Show.reservation_open() checks each event
        event_reservations = (
            ReservationPayment.objects.filter(
                reservation__event=OuterRef("pk"),
                status=PaymentStatus.CONFIRMED,
            )
            .values("reservation__event")
            .annotate(count=Count("reservation", distinct=True))
            .values("count")
        )

        event_guests = (
            Guest.objects.filter(
                event_reservation__event=OuterRef("pk"),
                event_reservation__reservationpayment__status=PaymentStatus.CONFIRMED,
            )
            .values("event_reservation__event")
            .annotate(count=Count("pk", distinct=True))
            .values("count")
        )

        events_queryset = Event.objects.order_by("admission").annotate(
            annotated_reservation_count=Coalesce(
                Subquery(event_reservations, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
            + Coalesce(
                Subquery(event_guests, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            )
        )

        qs = qs.prefetch_related(Prefetch("events", queryset=events_queryset)).annotate(
            next_event_begin=Min("events__begin"),
            annotated_total_capacity=Coalesce(
                Subquery(capacity_subquery, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            annotated_confirmed_reservations=Coalesce(
                Subquery(all_reservations_subquery, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            annotated_confirmed_guests=Coalesce(
                Subquery(all_guests_subquery, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        if "o" not in request.GET and getattr(self, "default_ordering", None):
            qs = qs.order_by(*self.default_ordering)
        return qs

    @admin.display(ordering="next_event_begin", description="Next event")
    def next_event_date(self, obj):
        next_begin = getattr(obj, "next_event_begin", None)
        if not next_begin:
            return "-"
        return timezone.localtime(next_begin).strftime("%d.%m.%y %H:%M")


class UpcomingShowAdmin(ShowAdmin):
    default_ordering = [F("next_event_begin").asc(nulls_last=True), "title"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        now = timezone.now()
        return qs.filter(Q(next_event_begin__gte=now) | Q(next_event_begin__isnull=True))


admin.site.register(Show, ShowAdmin)
