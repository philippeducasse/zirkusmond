import uuid

from django.db import models
from markdownx.models import MarkdownxField
from image_cropping import ImageRatioField


class Show(models.Model):  # maybe call it an event?
    ''' This is a show, with it's description, picture blablabla
        every showing of this show is an Event
    '''
    title = models.CharField(max_length=255)
    description = MarkdownxField()

    banner_link = models.ImageField()
    head_img = ImageRatioField('banner_link', '400x225')

    def __str__(self):
        return self.title

    def dates_text(self):
        # TODO
        return "No Shows Possible"


class Event(models.Model):
    """ An event
        everything that people would come to
    """
    show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True)
    begin = models.DateTimeField('einlass')
    end = models.DateTimeField('schluss')

    # how many people can come
    reservation_capacity = models.PositiveIntegerField(default=150)
    open_for_reservation = models.BooleanField(default=True)
    reservation_price = models.DecimalField(decimal_places=2, max_digits=4,
                                            default=5)

    def __str__(self):
        # return '%s at %s' % (self.show, self.begin.strftime('%D %H:%M'))
        return self.begin.strftime('%d.%m.%y at %H:%M')

    def reservation_open(self) -> bool:
        ''' can you register, still open spots?
        '''
        if not self.open_for_reservation:
            return False

        # TODO how many people registered, free spaces?
        # TODO is the event in the future?
        print('WARNING: '
              + 'Reservations not counted '
              + '[events.models.Event.reservation_open]')
        return True


class Person(models.Model):
    firstname = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)

    street = models.CharField(max_length=50, null=True)
    zipcode = models.PositiveIntegerField(null=True)
    town = models.CharField(max_length=25, null=True)

    email = models.EmailField(null=True, blank=True)
    phonenumber = models.CharField(max_length=25, null=True, blank=True)


class Reservation(models.Model):
    ''' People have to register for an event and provide their data
    '''
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#primary-key
    # TODO
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    # the person making the reservation
    reservant = models.ForeignKey(Person, on_delete=models.CASCADE)

    def guest_count(self):
        ''' for how many people do we reserve?
        '''
        return 3  # TODO TODO TODO

    # notizen, nachricht an uns
    # def __str__(self):
    #     return 'Reg %s, %s for %s' % (
    #         self.surname, self.firstname, self.event)


class Guest(Person):
    ''' All the data we get about our guest
        each guest instance belongs to a reservation
    '''
    event_reservation = models.ForeignKey(Reservation,
                                          on_delete=models.CASCADE)


from decimal import Decimal

from payments import PurchasedItem
from payments.models import BasePayment


class ReservationPayment(BasePayment):
    # TODO
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, null=True,
                                    on_delete=models.SET_NULL)

    def get_failure_url(self):
        return '/payment-failure/%s' % self.pk

    def get_success_url(self):
        return '/payment-success/%s' % self.pk

    def get_purchased_items(self):
        ''' yield a list of PurchasedItems
        '''
        yield PurchasedItem(name=str(self.reservation.event),
                            sku=self.reservation.event.pk,
                            quantity=self.reservation.guest_count(),
                            price=self.reservation.event.reservation_price,
                            currency='EUR')

    def from_reservation(reservation: Reservation, *args, **kwargs):
        self = ReservationPayment(*args, **kwargs)
        import pdb
        pdb.set_trace()
        self.reservation = reservation
        r = reservation.reservant
        self.billing_first_name = r.firstname
        self.billing_last_name = r.surname
        self.billing_address_1 = r.street
        self.billing_postcode = r.zipcode
        self.billing_city = r.town
        self.billing_email = r.email
        self.description = 'Reservations for %s' % reservation.event
        self.total = self.reservation.guest_count() * self.reservation.event.reservation_price
        self.currency = 'EUR'

        return self
        # customer_ip_address
