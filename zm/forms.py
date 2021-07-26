from django.forms import ModelForm

from .models import NewsletterRegistration

class NewsletterRegistrationForm(ModelForm):
    class Meta:
        model = NewsletterRegistration
        fields = ['email']
