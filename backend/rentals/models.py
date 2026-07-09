from django.db import models
from tinymce import models as tinymce_models


class RentalObject(models.Model):
    name = models.CharField(max_length=255)
    description = tinymce_models.HTMLField()
    image = models.ImageField()
    link = models.CharField(max_length=255, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def lastmod(self) -> str:
        return self.last_modified.strftime("%Y-%m-%d")
