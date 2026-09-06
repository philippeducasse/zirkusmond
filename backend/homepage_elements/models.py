from django.db import models
from tinymce import models as tinymce_models


class HomePageElement(models.Model):
    title = models.CharField(max_length=100)
    message = tinymce_models.HTMLField(max_length=1000)
    active = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


class PopUpElement(HomePageElement):
    class Position(models.TextChoices):
        TOP = "top"
        BOTTOM = "bottom"
        TOP_RIGHT = "top_right"
        BOTTOM_RIGHT = "bottom_right"

    position = models.CharField(max_length=50, choices=Position, default=Position.BOTTOM_RIGHT)
