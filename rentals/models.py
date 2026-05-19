from django.db import models
from markdownx.models import MarkdownxField


class RentalObject(models.Model):
    name = models.CharField(max_length=255)
    description = MarkdownxField()
    image = models.ImageField()
    link = models.CharField(max_length=255, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def lastmod(self):
        return self.last_modified.strftime('%Y-%m-%d')
