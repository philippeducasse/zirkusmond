from django.db import models


class Visitor(models.Model):
    '''
    '''
    useragent = models.TextField()
    ip = models.GenericIPAddressField()
    referer = models.URLField()
    time = models.DateTimeField()


class NewsletterRegistration(models.Model):
    ''' collect email addresses that shall be added to our mailing list
    '''
    email = models.EmailField()
