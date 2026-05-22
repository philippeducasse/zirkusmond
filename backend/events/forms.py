from django.forms import ModelForm, Form, ModelChoiceField, IntegerField, \
    BooleanField, Select, CharField
from tinymce.widgets import TinyMCE
from .models import Person, Event, Guest
from shows.models import Show

from django.core.exceptions import ValidationError




class EventModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj}' if obj.reservation_open() else f'RESERVATION CLOSED - {obj}'


class ReservationForm(Form):
    '''
    '''
    event = ModelChoiceField(None)
    attendee_count = IntegerField(min_value=1, max_value=10,
                                  initial=1, label="Tickets")

    def __init__(self, show: Show, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_events = Event.objects.filter(show=show.pk)
        open_ids = [e.pk for e in all_events if e.reservation_open()]
        choices = Event.objects.filter(pk__in=open_ids)
        self.fields['event'] = EventModelChoiceField(choices)
        #for i in choices:
        #    if not i.reservation_open():
        #        self.fields['event'].disabled_choices.append(str(i))


    def clean(self):
        cleaned_data = super().clean()

        # no more covid
        #if not cleaned_data['covid_stuff']:
        #    self.add_error('covid_stuff', 'You will have to be tested/vaccinated for the event')
        if not cleaned_data['event'].reservation_open():
            self.add_error('event', 'Sorry, Reservation for this Event is closed')
            raise ValidationError("Registration is closed, sorry :(")


class PersonForm(ModelForm):
    ''' Person Form
    '''
    class Meta:
        model = Person
        fields = ['firstname', 'surname', 'street', 'zipcode',
                  'town', 'email', 'phonenumber']

    def line_tuples(self):
        return ((self['firstname'], self['surname']),
                #(self['street'], self['zipcode'], self['town']),
                (self['email'], self['phonenumber']))

    def clean(self):
        cleaned_data = super().clean()

        for f in ['firstname', 'surname', 'email']:
            if f not in cleaned_data.keys():
                self.add_error(f, 'Missing')
            else:
                if cleaned_data[f] == None or cleaned_data[f] == '':
                    self.add_error(f, 'Not Set')


class GuestForm(ModelForm):
    ''' Person Form
    '''
    class Meta:
        model = Guest
        name_address_fields = ['firstname', 'surname',
                               'street', 'zipcode', 'town']
        name_fields = ['firstname', 'surname']
        fields =  name_fields

    def line_tuples(self):
        return ((self['firstname'], self['surname']),
                #(self['street'], self['zipcode'], self['town']),
                )

    def clean(self):
        cleaned_data = super().clean()

        for f in self.Meta.name_fields:
            if f not in cleaned_data.keys():
                self.add_error(f, 'Please give the names of your guests')
            else:
                if cleaned_data[f] == None or cleaned_data[f] == '':
                    self.add_error(f, 'Please give the names of your guests')
        #return cleaned_data

        #for f in self.Meta.name_address_fields:
        #    if f not in cleaned_data.keys():
        #        self.add_error(f, 'Missing')
        #    else:
        #        if cleaned_data[f] == None or cleaned_data[f] == '':
        #            self.add_error(f, 'Not Set')

#        if (('email' not in cleaned_data.keys() and
#             'phonenumber' not in cleaned_data.keys()) or
#            ((cleaned_data['email'] == None or cleaned_data['email'] == '') and
#             (cleaned_data['phonenumber'] is None or cleaned_data['phonenumber'] ==''))):
#            self.add_error('email', 'We need an Email or phonenumber')


class EmailTextForm(Form):
    subject = CharField(max_length=255, help_text="Subject")
    text_field = CharField(widget=TinyMCE())
