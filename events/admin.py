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
        print(queryset)
        l = []
        for i in queryset:
            if i.event() == self.value():
                l.append(i)
        #return l
        #return queryset
        return queryset.filter(
            Q(reservation__event=self.value()) |
            Q(guest__event_reservation__event=self.value()))
        return queryset.filter(reservation__event=self.value()) + queryset.filter(guest__event_reservation__event=self.value())


#class InlineCheckin(admin.StackedInline):
#    model = Checkin
#    extra = 1

class PersonAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'surname', 'email', 'phonenumber', 'event']#, 'check-ins']
    # list_filter = ('event')
    list_filter = (EventFilter,)
    search_fields = ['surname', 'firstname', 'email', 'phonenumber']
 #   inlines = [InlineCheckin]


admin.site.register(Show, MarkdownxModelAdmin)
admin.site.register(Event)
admin.site.register(Reservation)
admin.site.register(ReservationPayment)
admin.site.register(Guest)
admin.site.register(Person, PersonAdmin)
