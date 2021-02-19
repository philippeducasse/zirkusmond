from django.forms import ModelForm, Form, ModelChoiceField, IntegerField
from .models import Person, Event, Show, Guest


class ReservationForm(Form):
    '''
    '''
    event = ModelChoiceField(None)
    attendee_count = IntegerField(min_value=1, max_value=10,
                                  initial=1)

    def __init__(self, show: Show, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'] = ModelChoiceField(
            Event.objects.filter(
                show=show.pk))


class PersonForm(ModelForm):
    ''' Person Form
    '''
    class Meta:
        model = Person
        fields = ['firstname', 'surname', 'street', 'zipcode',
                  'town', 'email', 'phonenumber']


class GuestForm(ModelForm):
    ''' Person Form
    '''
    class Meta:
        model = Guest
        fields = ['firstname', 'surname', 'street', 'zipcode',
                  'town', 'email', 'phonenumber']
