from django.contrib import admin

from reservations.models import Guest, Reservation
from events import services


class InlineGuest(admin.StackedInline):
    model = Guest
    extra = 0


class ReservationAdmin(admin.ModelAdmin):
    inlines = (InlineGuest,)
    actions = ["resend_confirmation_mail"]
    search_fields = ["first_name", "last_name"]

    @admin.action(description="Resend Reservation confirmation mail")
    def resend_confirmation_mail(self, request, queryset):
        for reservation in queryset:
            services.send_confirmation_mail(reservation)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Guest)