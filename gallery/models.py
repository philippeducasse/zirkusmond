from django.db import models


class Album(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    hide = models.BooleanField(default=True)
    cover = models.ForeignKey("gallery.Foto", null=True, on_delete=models.SET_NULL,
                              blank=True)

    def __str__(self):
        return self.name


class Foto(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField()
    photographer = models.CharField(max_length=255, null=True, blank=True)
    saison = models.CharField(max_length=30, null=True, blank=True)  # 2018
    album_ref = models.ForeignKey(Album, null=True, on_delete=models.SET_NULL,
                              blank=True)
