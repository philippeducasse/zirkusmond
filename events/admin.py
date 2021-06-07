from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Show, Event, Person, Guest, Reservation, ReservationPayment

from django.db.models import Q


class EventFilter(admin.SimpleListFilter):
    '''
    '''
    title = 'Event'
    parameter_name = 'event_id'
    def lookups(self, request, model_admin):
        '''
        '''
        a = Event.objects.all()
        b = list(map(lambda x: (x.id, str(x)), Event.objects.all()))
        import pdb
        #pdb.set_trace()
        return b

    def queryset(self, request, queryset):
        '''
        '''
        return queryset.filter(
            Q(reservation__event=self.value()) |
            Q(guest__event_reservation__event=self.value()))


class EventAdmin(admin.ModelAdmin):
    '''
    '''
    list_display = ['show', 'begin', 'time_and_date',
                    'reservation_capacity', 'open_for_reservation',
                    'reservation_open', 'reservation_count']
    # list_filter = ('show',)

#class InlineCheckin(admin.StackedInline):
#    model = Checkin
#    extra = 1

class PersonAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'surname', 'email', 'phonenumber', 'event']#, 'check-ins']
    # list_filter = ('event')
    list_filter = (EventFilter,)
    search_fields = ['surname', 'firstname', 'email', 'phonenumber']
 #   inlines = [InlineCheckin]

class InlineGuest(admin.StackedInline):
    model = Guest
    extra = 0

class InlinePerson(admin.StackedInline):
    model = Person
    extra = 0

class ReservationPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reservation',
        'status',
        'ticket_count',
                    #'reservation__reservant__firstname', 'reservation__reservant__surname',
                    ]
    list_filter = ('status',) # EventFilter)
    search_fields = ['reservation__reservant__firstname', 'reservation__reservant__surname']

    actions = ['resend_confirmation_mail']
    @admin.action(description='Resend confirmation E-Mail')
    def resend_confirmation_mail(self, request, queryset):
        for i in queryset:
            i.reservation.send_confirmation_mail()

class ReservationAdmin(admin.ModelAdmin):
    # inlines = (InlinePerson, InlineGuest,)
    inlines = (InlineGuest,)
    actions = ['resend_confirmation_mail']
    search_fields = ['reservant__firstname', 'reservant__surname']

    @admin.action(description='Resend Reservation confirmation mail')
    def resend_confirmation_mail(self, request, queryset):
        for i in queryset:
            i.send_confirmation_mail()

class ShowAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'dates_text', 'reserved_tickets']

admin.site.register(Show, ShowAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReservationPayment, ReservationPaymentAdmin)
admin.site.register(Guest)
admin.site.register(Person, PersonAdmin)
