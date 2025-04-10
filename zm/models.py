from django.db import models
from markdownx.models import MarkdownxField


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

class RentalObject(models.Model):  # maybe call it an event?
    ''' Something that can be rented from zm, appears on the rentals page
    '''
    name = models.CharField(max_length=255)
    description = MarkdownxField()
    image = models.ImageField()
    link = models.CharField(max_length=255, blank=True )
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def lastmod(self):
        ''' lastmod string for sitemap
        '''
        return self.last_modified.strftime('%Y-%m-%d')