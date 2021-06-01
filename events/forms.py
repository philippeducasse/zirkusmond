from django.forms import ModelForm, Form, ModelChoiceField, IntegerField, BooleanField
from .models import Person, Event, Show, Guest


class ReservationForm(Form):
    '''
    '''
    event = ModelChoiceField(None)
    attendee_count = IntegerField(min_value=1, max_value=10,
                                  initial=1, label="Tickets")
    covid_stuff = BooleanField(initial=False, label="covid tested/vaccinated")

    def __init__(self, show: Show, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'] = ModelChoiceField(
            Event.objects.filter(
                show=show.pk))

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['covid_stuff']:
            self.add_error('covid_stuff', 'You will have to be tested/vaccinated for the event')
        if not cleaned_data['event'].reservation_open():
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
                (self['street'], self['zipcode'], self['town']),
                (self['email'], self['phonenumber']))

    def clean(self):
        cleaned_data = super().clean()

        for f in self.Meta.fields:
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
        fields = ['firstname', 'surname', 'street', 'zipcode',
                  'town', 'email', 'phonenumber']

    def line_tuples(self):
        return ((self['firstname'], self['surname']),
                (self['street'], self['zipcode'], self['town']),
                (self['email'], self['phonenumber']))

    def clean(self):
        cleaned_data = super().clean()

        for f in self.Meta.fields:
            if f not in cleaned_data.keys():
                self.add_error(f, 'Missing')
            else:
                if cleaned_data[f] == None or cleaned_data[f] == '':
                    self.add_error(f, 'Not Set')
