from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, IntegerField, CharField
from tinymce.widgets import TinyMCE

from .models import Event
from reservations.models import Guest, Reservation
from shows.models import Show

from django.forms import ModelChoiceField


class EventModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj}' if obj.reservation_open() else f'RESERVATION CLOSED - {obj}'


class ReservationForm(ModelForm):
    attendee_count = IntegerField(min_value=1, max_value=10, initial=1, label="Tickets")

    class Meta:
        model = Reservation
        fields = ['event', 'first_name', 'last_name', 'email']

    def __init__(self, show: Show, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_events = Event.objects.filter(show=show.pk)
        open_ids = [e.pk for e in all_events if e.reservation_open()]
        self.fields['event'] = EventModelChoiceField(Event.objects.filter(pk__in=open_ids))

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        if event and not event.reservation_open():
            self.add_error('event', 'Sorry, Reservation for this Event is closed')
            raise ValidationError("Registration is closed, sorry :(")


class GuestForm(ModelForm):
    class Meta:
        model = Guest
        name_fields = ['first_name', 'last_name']
        fields = name_fields

    def line_tuples(self):
        return ((self['first_name'], self['last_name']),)

    def clean(self):
        cleaned_data = super().clean()
        for field in self.Meta.name_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'Please give the names of your guests')


class EmailTextForm(Form):
    subject = CharField(max_length=255, help_text="Subject")
    text_field = CharField(widget=TinyMCE())