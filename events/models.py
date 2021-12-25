import uuid

from django.db import models
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.urls import reverse

from markdownx.models import MarkdownxField
from image_cropping import ImageRatioField

from decimal import Decimal
from payments import PaymentError, PaymentStatus
from payments import PurchasedItem
from payments.models import BasePayment

from django.core.mail import send_mail


class Show(models.Model):
    ''' This is a show, with it's description, picture blablabla
        every showing of this show is an Event
    '''
    title = models.CharField(max_length=255)
    description = MarkdownxField()

    banner_link = models.ImageField()
    head_img = ImageRatioField('banner_link', '400x225')

    private = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)

    def events(self):
        return Event.objects.filter(show=self).order_by('admission')

    def last_event(self):
        return self.events().first()

    def first_event(self):
        return self.events().last()

    def __str__(self):
        return self.title

    def dates_text(self):
        # TODO
        return '/'.join(map(str, self.events()))

    def lastmod(self):
        ''' lastmod string for sitemap
        '''
        return self.last_modified.strftime('%Y-%m-%d')

    @admin.display
    def reserved_tickets(self):
        events = Event.objects.filter(show=self)
        available = sum(map(lambda x: x.reservation_capacity, events))
        reserved = sum(map(lambda x: x.reservation_count(), events))
        return f'{reserved}/{available}'

    @admin.display(boolean=True)
    def reservation_open(self) -> bool:
        return any(list(map(lambda x: x.reservation_open(), self.events())))


class Event(models.Model):
    """ An event
        everything that people would come to
    """
    show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True)
    admission = models.DateTimeField('Admission')
    begin = models.DateTimeField('Show Begins')
    end = models.DateTimeField('schluss', null=True)

    # how many people can come
    reservation_capacity = models.PositiveIntegerField(default=150)
    open_for_reservation = models.BooleanField(default=True)
    reservation_price = models.DecimalField(decimal_places=2, max_digits=4,
                                            default=5)

    def __str__(self):
        # return '%s at %s' % (self.show, self.begin.strftime('%D %H:%M'))
        return self.admission.astimezone().strftime('%d.%m.%y at %H:%M')

    @admin.display
    def time_and_date(self):
         return self.admission.astimezone().strftime('%d.%m.%y at %H:%M')

    def admission_time(self):
        return self.admission.astimezone().strftime('%H:%M')

    @admin.display(boolean=True)
    def reservation_open(self) -> bool:
        ''' can you register, still open spots?
        '''
        if not self.open_for_reservation:
            return False

        if self.reservation_count() > self.reservation_capacity:
            return False

        if timezone.now() > self.begin:
            return False

        return True

    @admin.display
    def reservation_count(self):
        return sum(map(lambda x: x.reservation.ticket_count(), ReservationPayment.objects.filter(reservation__event=self, status=PaymentStatus.CONFIRMED),))

    @admin.display
    def reserved_tickets(self):
        return f'{self.reservation_count()}/{self.reservation_capacity}'


class Person(models.Model):
    firstname = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)

    street = models.CharField(max_length=50, null=True)
    zipcode = models.PositiveIntegerField(null=True)
    town = models.CharField(max_length=25, null=True)

    email = models.EmailField(null=True, blank=True)
    phonenumber = models.CharField(max_length=25, null=True, blank=True)

    @admin.display
    def event(self):
        r = Reservation.objects.filter(reservant=self)
        if len(r) == 0:
            r = Guest.objects.filter(id=self.id)
            if len(r) == 0:
                #import pdb
                #pdb.set_trace()
                return None
            return r[0].event_reservation.event
        return r[0].event

    def __str__(self):
        return '%s %s' % (self.firstname, self.surname)

class Reservation(models.Model):
    ''' People have to register for an event and provide their data
    '''
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#primary-key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    # the person making the reservation
    reservant = models.ForeignKey(Person, on_delete=models.CASCADE)

    def guests(self):
        return Guest.objects.filter(event_reservation=self)

    @admin.display
    def ticket_count(self):
        ''' for how many people do we reserve?
        '''
        return len(Guest.objects.filter(event_reservation=self)) + 1

    # notizen, nachricht an uns
    def __str__(self):
        return 'Reg %s, %s, %s Tickets for %s' % (
            self.reservant.surname, self.reservant.firstname, self.ticket_count(), self.event)

    def send_confirmation_mail(self):
        p = self.reservant
        show = self.event.show
        attendants = '\n%s %s\n%s %s %s\n%s %s'% (
                        p.firstname, p.surname,
                        p.street, p.zipcode, p.town,
                        p.email, p.phonenumber)
        for a in self.guests():
            attendants += '\n\n%s %s\n%s %s %s\n%s %s' % (
                a.firstname, a.surname,
                a.street, a.zipcode, a.town,
                a.email, a.phonenumber)
        s_title = self.event.time_and_date()

        send_mail(
                            'Thank you for your Reservation for %s' % show.title,
"""Dear %s,

thank you for your reservation to %s!

You have booked your visit for %s with the following personal information:
%s

We open our gates at %s, the Show will start at %s.

Please note the following:
- Be on time, make sure that you have a valid Covid-19 test (24h fresh) and confirmation that you are fully vaccinated or recovered.
- Also please remember that we dont have a box office for later registration and due to the Covid-19 rules of Berlin we can’t let in more than 150 people. So tell your friends that they have to register through this form!

See you at Zirkus Mond and have fun.
 <3
 """ % ( #  - On the site you are allowed to wander freely around but please remember to wear your mask at all times when distance to others can not be garanteed
        p.firstname,
        show.title,
        s_title,
        attendants,
        self.event.admission.astimezone().strftime('%H:%M'),
        self.event.begin.astimezone().strftime('%H:%M')),
            'reservation@zirkusmond.de',
            [p.email])


class Guest(Person):
    ''' All the data we get about our guest
        each guest instance belongs to a reservation
    '''
    event_reservation = models.ForeignKey(Reservation,
                                          on_delete=models.CASCADE)


class ReservationPayment(BasePayment):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, null=True,
                                    on_delete=models.SET_NULL)

    def get_failure_url(self):
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}/payment-failure/%s' % self.pk

    def get_success_url(self):
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}/payment-success/%s' % self.pk

    def get_process_url(self) -> str:
        prot = 'https' if settings.PAYMENT_USES_SSL else 'http'
        return f'{prot}://{settings.PAYMENT_HOST}' + reverse('process_payment', kwargs={'token': self.token})

    def get_purchased_items(self):
        ''' yield a list of PurchasedItems
        '''
        yield PurchasedItem(name=f'{self.reservation.event.show.title} {self.reservation.event}',
                            sku=self.reservation.event.pk,
                            quantity=self.reservation.ticket_count(),
                            price=self.reservation.event.reservation_price,
                            currency='EUR')

    def from_reservation(reservation: Reservation, *args, **kwargs):
        self = ReservationPayment(*args, **kwargs)
        import pdb
        #pdb.set_trace()
        self.reservation = reservation
        r = reservation.reservant
        self.billing_first_name = r.firstname
        self.billing_last_name = r.surname
        self.billing_address_1 = r.street
        self.billing_postcode = r.zipcode
        self.billing_city = r.town
        self.billing_email = r.email
        self.description = 'Reservations for %s' % reservation.event
        self.total = self.reservation.ticket_count() * self.reservation.event.reservation_price
        self.currency = 'EUR'

        return self

    @admin.display
    def ticket_count(self):
        return self.reservation.ticket_count()

    @admin.display
    def event(self):
        return f'{self.reservation.event}'


class NewsletterEmail(models.Model):
    ''' Save E-Mails of people
    '''
    email = models.EmailField()
