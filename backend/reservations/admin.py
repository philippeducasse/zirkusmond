from django.contrib import admin
from django.utils import timezone

from events import services
from events.models import Event
from reservations.models import Guest, PastReservation, Reservation, UpcomingReservation


class InlineGuest(admin.StackedInline):
    model = Guest
    extra = 0


class BaseReservationAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "email",
        "event",
        "ticket_count",
        "checked_in",
    ]
    inlines = (InlineGuest,)
    actions = ["resend_confirmation_mail"]
    search_fields = ["first_name", "last_name", "email"]

    @admin.display(ordering="last_name")
    def last_name(self, obj):
        return obj.last_name

    @admin.display(ordering="first_name")
    def first_name(self, obj):
        return obj.first_name

    @admin.display(ordering="email")
    def email(self, obj):
        return obj.email

    @admin.display(ordering="checked_in")
    def checked_in(self, obj):
        return obj.checked_in

    checked_in.boolean = True

    @admin.action(description="Resend Reservation confirmation mail")
    def resend_confirmation_mail(self, request, queryset):
        for reservation in queryset:
            services.send_confirmation_mail(reservation)


class ReservationAdmin(BaseReservationAdmin):
    ordering = ["-event__begin"]
    fields = ["event", "first_name", "last_name", "email", "checked_in"]
    readonly_fields = ["event"]


class UpcomingReservationAdmin(BaseReservationAdmin):
    ordering = ["-event__begin"]
    fields = ["event", "first_name", "last_name", "email", "checked_in"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(begin__gte=timezone.now())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PastReservationAdmin(BaseReservationAdmin):
    ordering = ["-event__begin"]
    fields = ["event", "first_name", "last_name", "email", "checked_in"]
    readonly_fields = ["event"]


class GuestAdmin(admin.ModelAdmin):
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

    @admin.display(ordering="last_name")
    def last_name(self, obj):
        return obj.last_name

    @admin.display(ordering="first_name")
    def first_name(self, obj):
        return obj.first_name

    @admin.display(ordering="checked_in")
    def checked_in(self, obj):
        return obj.checked_in

    checked_in.boolean = True


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(UpcomingReservation, UpcomingReservationAdmin)
admin.site.register(PastReservation, PastReservationAdmin)
admin.site.register(Guest, GuestAdmin)
