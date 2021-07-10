# from django.shortcuts import render
from .models import Show, Event, Reservation, Guest, NewsletterEmail
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

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
    newsletter = False
    if request.method == 'POST':
        rForm = ReservationForm(show, request.POST, prefix='res')
        pForm = PersonForm(request.POST, prefix='pers')
        import pdb
        # pdb.set_trace()
        if 'newsletter' in request.POST:
            newsletter = request.POST['newsletter'] # == 'on'
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

                        if newsletter:
                            n = NewsletterEmail(email=p.email)
                            n.save()

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
        GuestFormSet = formset_factory(GuestForm, max_num=0,
                                           extra=0, min_num=0,
                                           validate_min=True)

        dgForms = GuestFormSet(prefix='gues')

    return render(request, 'reserve.html',
                  {'show': show,
                   'rForm': rForm,
                   'pForm': pForm,
                   'gForms': dgForms,
                   'newsletter': newsletter,
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
        payment.reservation.send_confirmation_mail()
    return redirect('/reservation_status/%s' % payment.id)


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
