# from django.shortcuts import render
from .models import Show, Event, Reservation, Guest
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from django.core.mail import send_mail

from .forms import ReservationForm, PersonForm, GuestForm
from django.forms import formset_factory


from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded
from .models import ReservationPayment


def _get_ip(request):
    ''' fetches the user ip
    '''
    key = 'HTTP_X_REAL_IP' if 'HTTP_X_REAL_IP' in request.META.keys() else 'REMOTE_ADDR'
    return request.META[key]


def show(request, show_id):
    ''' show show details page for a given id
    '''
    try:
        s = Show.objects.get(id=show_id)
    except Exception as e:
        print(e)
        raise Http404("Show does not exist")

    return render(request, 'show.html',
                  {'show': s})


def event(request, event_id):
    ''' Show Event details
    '''
    e = get_object_or_404(Event, event_id)
    return render(request, 'event.html',
                  {'event': e})


def reserve(request, show_id):
    ''' reserve stuff for show
    '''
    show = get_object_or_404(Show, pk=show_id)
    if request.method == 'POST':
        rForm = ReservationForm(show, request.POST, prefix='res')
        pForm = PersonForm(request.POST, prefix='pers')
        import pdb
        # pdb.set_trace()
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
                        variant = request.POST['payment-method']
                        rP = ReservationPayment.from_reservation(r,
                                 variant=variant,
                                 customer_ip_address=_get_ip(request))
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


#
#   Payment
#
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


def reservation_status(request, payment_id):
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    show = payment.reservation.event.show
    
    return TemplateResponse(request, 'reservation_status.html',
                            {'payment': payment,
                             'show': show})


def payment_success(request, payment_id):
    payment = get_object_or_404(ReservationPayment, id=payment_id)
    show = payment.reservation.event.show
    p = payment.reservation.reservant
    if payment.status == 'confirmed':
        attendants = '%s %s\n%s %s %s\n%s %s'% (
                            p.firstname, p.surname,
                            p.street, p.zipcode, p.town,
                            p.email, p.phonenumber)
        for a in payment.reservation.guests():
            attendants += '\n%s %s\n%s %s %s\n%s %s' % (
                a.firstname, a.surname,
                a.street, a.zipcode, a.town,
                a.email, a.phonenumber)
        s_title = payment.reservation.event.time_and_date()

        send_mail(
                            'Thank you for your Reservation for %s' % show.title,
"""Dear %s,

thank you for your reservation to %s!

You have booked your visit for %s with the following personal information:
%s

We open our gates at %s, the Show will start at %s.

Please note the following:
- Be on time, make sure that you have a valid Covid-19 test (24h fresh) or confirmation that you are fully vaccinated.
- Also please remember that we dont have a box office for later registration and due to the Covid-19 rules of Berlin we can’t let in more than 150 people. So tell your friends that they have to register through this form!

See you at Zirkus Mond and have fun.
 <3
 """ % ( #  - On the site you are allowed to wander freely around but please remember to wear your mask at all times when distance to others can not be garanteed
        p.firstname,
        show.title,
        s_title,
        attendants,
        payment.reservation.event.admission.astimezone().strftime('%H:%M'),
        payment.reservation.event.begin.astimezone().strftime('%H:%M')),
            'reservation@zirkusmond.de',
            [p.email])
    return redirect('/reservation_status/%s' % payment.id)
    return TemplateResponse(request, 'reservation_status.html',
                            {'payment': payment,
                             'show': show})
    return HttpResponse('Successfully payed %s' % payment_id)


def payment_fail(request, payment_id):
    p = get_object_or_404(ReservationPayment, id=payment_id)
    return TemplateResponse(request, 'payment_failure.html',
                            {'payment': p})

# class CreateReservationView(CreateView):
#     ''' make a reservation for a show
#     '''
#     model = Reservation
#     template_name = 'reservation'
#     form_class =
# #    def form_valid(self, form):
# #        return super().form_valid(form)
