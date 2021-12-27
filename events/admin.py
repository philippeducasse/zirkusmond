from django.contrib import admin
from django.utils import timezone
from django.db.models.functions import Lower
from markdownx.admin import MarkdownxModelAdmin
from .models import Show, Event, Person, Guest, Reservation, ReservationPayment, NewsletterEmail
from payments import PaymentStatus
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context, Template

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q
from django.conf import settings
from .forms import EmailTextForm

from io import BytesIO
import xlsxwriter

import imaplib
import time

def reservation_to_dict(reservation):
    ''' make a dict with most important reservation infos
        usefull for templates
    '''
    return {'show_title': reservation.event.show.title,
            'event_time': reservation.event.time_and_date(),
            'firstname': reservation.reservant.firstname,
            'surname': reservation.reservant.surname,
            'email': reservation.reservant.email}


def render_mail(subject, body, context):
    context = Context(context)
    ts = Template(subject)
    subject = ts.render(context)
    tb = Template(body)
    body = tb.render(context)
    return subject, body


def send_email_to_reservants(request, dicts, admin):
    if 'text_field' in request.POST.keys():
        form = EmailTextForm(request.POST)
    else:
        form = EmailTextForm()
    sample_text, sample_subject = None, ""
    if form.is_valid():
        mail_text = form.data['text_field']
        mail_subject = form.data['subject']
        sample_subject, sample_text = render_mail(mail_subject, mail_text, dicts[0])

        if 'send' in request.POST.keys():
            imap = imaplib.IMAP4(settings.EMAIL_HOST)
            imap.starttls()
            imap.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            for d in dicts:
                subject, text = render_mail(mail_subject, mail_text, d)
                m = EmailMessage(subject, text, 'reservation@zirkusmond.de',
                                 [f"{d['firstname']} {d['surname']} <{d['email']}>"])
                imap.append('Sent', '\\SEEN', imaplib.Time2Internaldate(time.time()), str(m.message()).encode())
                m.send()
            imap.logout()
            admin.message_user(request,f"Mail sent to {len(dicts)} recipients")
            return HttpResponseRedirect(request.get_full_path())


    return render(request, 'admin/send_email.html',
                context={'data': dicts,
                            'form': form,
                            'sample_text': sample_text,
                            'sample_subject': sample_subject,
                            'action': request.POST['action'],
                            'select_across': request.POST['select_across'],
                            'index': request.POST['index'],
                            'selected_action': request.POST.getlist('_selected_action')})


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


class ReservationPaymentEventFilter(admin.SimpleListFilter):
    '''Filter Reservation Payments for events
    '''
    title = 'Event'
    parameter_name = 'event'
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
        if self.value():
            return queryset.filter(reservation__event=self.value())
        else:
            return queryset


class EventAdmin(admin.ModelAdmin):
    '''
    '''
    list_display = ['show', 'begin', 'time_and_date',
                    'reservation_open', 'reserved_tickets']
    actions = ['print_reservations', 'send_to_reservants']


    @admin.action(description='Print Reservation List')
    def print_reservations(self, request, queryset):
        for event in queryset:
            rPs = ReservationPayment.objects.filter(reservation__event=event, status=PaymentStatus.CONFIRMED).order_by(Lower('reservation__reservant__firstname'))
            reservations = map(lambda x: x.reservation, rPs)

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.set_landscape()
            worksheet.set_paper(9) # A4
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

                add_row(worksheet, row, reservation.reservant)
                worksheet.write(row, 0, reservant.firstname, bold)

                row += 1

                for guest in Guest.objects.filter(event_reservation=reservation):
                    add_row(worksheet, row, guest)
                    row += 1

            workbook.close()
            xlsx_data = output.getvalue()

            filename = event.admission.astimezone().strftime('reservation_list_%Y-%m-%d.xlsx')
            response = HttpResponse(
                headers={'Content-Disposition': f'inline; filename="{filename}"'},
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.write(xlsx_data)
            return response

    @admin.action(description="Send mail to Reservants") #,help="Send an email to al the People who reserved")
    def send_to_reservants(self, request, queryset):
        events_reservations = []
        for event in queryset:
            events_reservations += list(ReservationPayment.objects.filter(status="confirmed",
                                                                          reservation__event=event))
        #events_reservation = sum(events_reservations ,[])
        dicts = [reservation_to_dict(r.reservation) for r in events_reservations]
        return send_email_to_reservants(request, dicts, self)

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
        'event',
                    #'reservation__reservant__firstname', 'reservation__reservant__surname',
                    ]
    list_filter = ('status', ReservationPaymentEventFilter) # EventFilter)
    search_fields = ['reservation__reservant__firstname', 'reservation__reservant__surname']

    actions = ['resend_confirmation_mail', 'send_to_reservants']
    @admin.action(description='Resend confirmation E-Mail')
    def resend_confirmation_mail(self, request, queryset):
        for i in queryset:
            i.reservation.send_confirmation_mail()

    @admin.action(description="Send mail to Reservants") #,help="Send an email to al the People who reserved")
    def send_to_reservants(self, request, queryset):
        import pdb
        dicts = [reservation_to_dict(o.reservation) for o in queryset]
        return send_email_to_reservants(request, dicts, self)

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
    list_display = ['title', 'dates_text', 'reserved_tickets', 'reservation_open']

class NewsletterRegistrationAdmin(admin.ModelAdmin):
    list_display = ('email',)
    actions = ['export_adresses']

    @admin.action(description="Export EMail Adresses")
    def export_adresses(self, request, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        data = map(lambda x: x.email, queryset)
        worksheet.write_column(0, 0, data)

        workbook.close()
        xlsx_data = output.getvalue()
        filename = timezone.now().strftime('email_addresses_%Y_%m_%d.xlsx')
        response = HttpResponse(
            headers={
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': f'attachment; filename={filename}',
                })
        response.write(xlsx_data)
        return response

admin.site.register(Show, ShowAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReservationPayment, ReservationPaymentAdmin)
admin.site.register(Guest)
admin.site.register(Person, PersonAdmin)
admin.site.register(NewsletterEmail, NewsletterRegistrationAdmin)
