from django.db import models


class Show(models.Model):  # maybe call it an event?
    ''' This is a show, with it's description, picture blablabla
        every showing of this show is an Event
    '''
    title = models.CharField(max_length=255)
    description = models.TextField()

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
    def __str__(self):
        return '%s at %s' % (self.show, self.begin)


class Registration(models.Model):
    ''' People have to register for an event and provide their data
    '''
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

    firstname = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)

    street = models.CharField(max_length=50)
    zipcode = models.PositiveIntegerField()
    town = models.CharField(max_length=25)

    email = models.EmailField()
    phonenumber = models.CharField(max_length=25)

    # notizen, nachricht an uns
    def __str__(self):
        return 'Reg %s, %s for %s' % (
            self.surname, self.firstname, self.event)
