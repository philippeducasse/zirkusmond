from django.forms import ModelForm, Form, ModelChoiceField, IntegerField, BooleanField, Select
from .models import Person, Event, Show, Guest

from django.core.exceptions import ValidationError


class EventSelect(Select):
    disabled_choices = []

    def render_option(self, name, value, attrs, renderer):
        print(type(self), self)
        print(name)
        print(attrs)
        print(type(renderer), renderer)
        if value in self.disabled_choices:
            attrs.update({'disabled':' disabled'})
        print(attrs)
        import pdb
        pdb.set_trace()
        return super().render_option(name, value, attrs, renderer)

class EventModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj}' if obj.reservation_open() else f'RESERVATION CLOSED - {obj}'

class ReservationForm(Form):
    '''
    '''
    event = ModelChoiceField(None)
    attendee_count = IntegerField(min_value=1, max_value=10,
                                  initial=1, label="Tickets")
    covid_stuff = BooleanField(initial=False, label="covid tested/vaccinated")

    def __init__(self, show: Show, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = Event.objects.filter(show=show.pk)
        self.fields['event'] = EventModelChoiceField(choices)
        #for i in choices:
        #    if not i.reservation_open():
        #        self.fields['event'].disabled_choices.append(str(i))


    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['covid_stuff']:
            self.add_error('covid_stuff', 'You will have to comply with the corona regulations.')
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
        name_address_fields = ['firstname', 'surname',
                               'street', 'zipcode', 'town']
        fields = name_address_fields + ['email', 'phonenumber']

    def line_tuples(self):
        return ((self['firstname'], self['surname']),
                (self['street'], self['zipcode'], self['town']),
                (self['email'], self['phonenumber']))

    def clean(self):
        cleaned_data = super().clean()

        for f in self.Meta.name_address_fields:
            if f not in cleaned_data.keys():
                self.add_error(f, 'Missing')
            else:
                if cleaned_data[f] == None or cleaned_data[f] == '':
                    self.add_error(f, 'Not Set')

        if (('email' not in cleaned_data.keys() and
             'phonenumber' not in cleaned_data.keys()) or
            ((cleaned_data['email'] == None or cleaned_data['email'] == '') and
             (cleaned_data['phonenumber'] is None or cleaned_data['phonenumber'] ==''))):
            self.add_error('email', 'We need an Email or phonenumber')
