from django.db import models


class NewsletterRegistration(models.Model):
    email = models.EmailField(unique=True)
