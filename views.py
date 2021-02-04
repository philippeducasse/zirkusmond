from django.shortcuts import render, get_object_or_404
from django.http import Http404
# from django import forms
from django.views.generic.edit import CreateView


# from .models import Article
from .events.models import Show, Event, Reservation


def plain(request):
    ''' Give em our index, without doing much
    '''
    us = Show.objects.all()
    return render(request, 'index.html',
                  {'upcoming_shows': us})


def show(request, show_id):
    ''' show show details page for a given id
    '''
    try:
        s = Show.objects.get(id=show_id)
    except:
        raise Http404("Show does not exist")

    return render(request, 'show.html',
                  {'show': s})


def event(request, event_id):
    ''' Show Event details
    '''
    e = get_object_or_404(Event, event_id)
    return render(request, 'event.html',
                  {'event': e})

from .events.forms import ReservationForm, PersonForm
from django.forms import formset_factory


def reserve(request, show_id):
    ''' reserve stuff for show
    '''
    show = get_object_or_404(Show, pk=show_id)
    if request.method == 'POST':
        rForm = ReservationForm(show, request.POST, prefix='res')
        pForm = PersonForm(request.POST, prefix='pers')
        try:
            gCount = int(rForm.data['res-attendee_count']) - 1

            GuestFormSet = formset_factory(PersonForm, max_num=gCount,
                                           extra=10, min_num=gCount,
                                           validate_min=True)

            if ('gues-INITIAL_FORMS' in request.POST
                and request.POST['gues-MAX_NUM_FORMS'] == str(gCount)):
                    dgForms = GuestFormSet(request.POST, prefix='gues')
            else:
                dgForms = GuestFormSet(prefix='gues')
        except KeyError:
            pass
    else:
        print(type(show), show)
        rForm = ReservationForm(show, prefix='res')
        pForm = PersonForm(prefix='pers')
        dgForms = None  # GuestFormSet(prefix='gues')

    return render(request, 'reserve.html',
                  {'show': show,
                   'rForm': rForm,
                   'pForm': pForm,
                   'gForms': dgForms
                   })

# class CreateReservationView(CreateView):
#     ''' make a reservation for a show
#     '''
#     model = Reservation
#     template_name = 'reservation'
#     form_class =
# #    def form_valid(self, form):
# #        return super().form_valid(form)
