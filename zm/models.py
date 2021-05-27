from django.db import models


class Visitor(models.Model):
    '''
    '''
    useragent = models.TextField()
    ip = models.GenericIPAddressField()
    referer = models.URLField()
    time = models.DateTimeField()
