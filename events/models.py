from django.db import models
from markdownx.models import MarkdownxField


class Show(models.Model):  # maybe call it an event?
    ''' This is a show, with it's description, picture blablabla
        every showing of this show is an Event
    '''
    title = models.CharField(max_length=255)
    description = MarkdownxField()

    banner_link = models.ImageField()

    def __str__(self):
        return self.title


class Event(models.Model):
    """ An event
        everything that people would come to
    """
    show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True)
    begin = models.DateTimeField('einlass')
    end = models.DateTimeField('schluss')

    # how many people can come
    reservation_capacity = models.PositiveIntegerField(default=True)
    open_for_reservation = models.BooleanField(default=True)

    def __str__(self):
        return '%s at %s' % (self.show, self.begin)

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

    street = models.CharField(max_length=50)
    zipcode = models.PositiveIntegerField()
    town = models.CharField(max_length=25)

    email = models.EmailField()
    phonenumber = models.CharField(max_length=25)


class Reservation(models.Model):
    ''' People have to register for an event and provide their data
    '''
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    # the person making the reservation
    reservant = models.ForeignKey(Person, on_delete=models.CASCADE)
    # def guest_count(self): TODO

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
