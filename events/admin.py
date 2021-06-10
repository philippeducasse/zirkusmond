from django.contrib import admin
from django.db.models.functions import Lower
from markdownx.admin import MarkdownxModelAdmin
from .models import Show, Event, Person, Guest, Reservation, ReservationPayment
from payments import PaymentStatus
from django.http import HttpResponse

from django.db.models import Q


from io import BytesIO
import xlsxwriter


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
    actions = ['print_reservations']


    @admin.action(description='Print Reservation List')
    def print_reservations(self, request, queryset):
        for event in queryset:
            rPs = ReservationPayment.objects.filter(reservation__event=event, status=PaymentStatus.CONFIRMED).order_by(Lower('reservation__reservant__firstname'))
            reservations = map(lambda x: x.reservation, rPs)

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.set_landscape()
            worksheet.set_paper(0) # A4
            worksheet.set_column(0, 5, 15)
            # worksheet.set_column(4, 5, 5)

            # Add a bold format to use to highlight cells.
            bold = workbook.add_format({'bold': True, 'border': 1})
            border = workbook.add_format({'border': 1})
            # Add a number format for cells with money.
            money = workbook.add_format({'num_format': '$#,##0'})


            columns = ['firstname', 'surname', 'address', 'phone', 'email', 'newsletter']
            def add_row(worksheet, row, person):
                worksheet.write_row(row, 0,
                    [person.firstname, person.surname, person.street, person.phonenumber, person.email],
                    border)

            worksheet.write_row(0, 0, columns, bold)
            worksheet.repeat_rows(0)
            row = 1
            for reservation in reservations:
                reservant = reservation.reservant
                print(reservation, type(reservation))
                add_row(worksheet, row, reservation.reservant)
                worksheet.write(row, 0, reservant.firstname, bold)

                row += 1

                for guest in Guest.objects.filter(event_reservation=reservation):
                    add_row(worksheet, row, guest)
                    row += 1

            workbook.close()
            xlsx_data = output.getvalue()

            response = HttpResponse(
                #headers={'Content_Disposition: inline; filename="myfile.txt"'},
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.write(xlsx_data)
            return response


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
