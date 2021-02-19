from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
# from django import forms
from django.views.generic.edit import CreateView


# from .models import Article
from .events.models import Show, Event, Reservation, Guest


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

from .events.forms import ReservationForm, PersonForm, GuestForm
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

            GuestFormSet = formset_factory(GuestForm, max_num=gCount,
                                           extra=10, min_num=gCount,
                                           validate_min=True)

            if ('gues-INITIAL_FORMS' in request.POST
                and request.POST['gues-MAX_NUM_FORMS'] == str(gCount)):
                    dgForms = GuestFormSet(request.POST, prefix='gues')

                    if rForm.is_valid() and pForm.is_valid() and dgForms.is_valid():
                        p = pForm.save()
                        r = Reservation(event=rForm.cleaned_data['event'], reservant=p)
                        r.save()
                        for g in dgForms:
                            g.event_reservation_id = r.pk
                            g.instance.event_reservation = r
                            g.save()
                        pass  # pay
                        rP = ReservationPayment.from_reservation(r,
                                 variant='default',  # TODO
                                 customer_ip_address=request.META['REMOTE_ADDR'])
                        rP.save()
                        return redirect('/payment/%s' % rP.pk)
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



from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded
from .events.models import ReservationPayment

def payment(request, payment_id, payment_variant=None):
    ''' handle payment
    '''
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    if payment_variant:
        payment.variant = payment_variant
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        print('REDIRECT NEEDED')
        return redirect(str(redirect_to))
    return TemplateResponse(request, 'payment.html',
                            {'form': form, 'payment': payment})


def payment_success(request, payment_id):
    return HttpResponse('Successfully payed %s' % payment_id)


def payment_fail(request, payment_id):
    p = get_object_or_404(ReservationPayment, payment_id)
    return HttpResponse('Failed to pay %s, status: %s' % (payment_id, p.status))

# class CreateReservationView(CreateView):
#     ''' make a reservation for a show
#     '''
#     model = Reservation
#     template_name = 'reservation'
#     form_class =
# #    def form_valid(self, form):
# #        return super().form_valid(form)
