import uuid
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from payments import PaymentStatus

from events.models import Event
from events import services
from reservations.models import Guest, Reservation, ReservationPayment
from shows.models import Show


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_image():
    buf = BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')


def make_show(**kwargs):
    defaults = dict(
        title='Test Show', description='', cast='',
        card_image=make_image(), private=False,
        base_ticket_price=15,
    )
    defaults.update(kwargs)
    return Show.objects.create(**defaults)


def make_event(show, offset_days=7, capacity=150):
    base = timezone.now() + timedelta(days=offset_days)
    return Event.objects.create(
        show=show,
        admission=base.replace(hour=19, minute=0, second=0, microsecond=0),
        begin=base.replace(hour=20, minute=0, second=0, microsecond=0),
        reservation_capacity=capacity,
        open_for_reservation=True,
    )


def make_reservation(event, **kwargs):
    defaults = dict(first_name='Test', last_name='User', email='test@example.com')
    defaults.update(kwargs)
    return Reservation.objects.create(event=event, **defaults)


# ---------------------------------------------------------------------------
# Reservation model
# ---------------------------------------------------------------------------

class ReservationModelTest(TestCase):
    def setUp(self):
        self.show = make_show()
        self.event = make_event(self.show)
        self.reservation = make_reservation(self.event)

    def test_ticket_count_no_guests(self):
        self.assertEqual(self.reservation.ticket_count(), 1)

    def test_ticket_count_with_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name='G', last_name='H')
        Guest.objects.create(reservation=self.reservation, first_name='I', last_name='J')
        self.assertEqual(self.reservation.ticket_count(), 3)

    def test_str_contains_event_and_name(self):
        result = str(self.reservation)
        self.assertIn('User', result)
        self.assertIn('Test', result)

    def test_guests_relation(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='G', last_name='H')
        self.assertIn(guest, self.reservation.guests.all())

    def test_checked_in_defaults_false(self):
        self.assertFalse(self.reservation.checked_in)

    def test_uuid_primary_key(self):
        self.assertIsNotNone(self.reservation.id)
        self.assertIsInstance(str(self.reservation.id), str)


# ---------------------------------------------------------------------------
# Guest model
# ---------------------------------------------------------------------------

class GuestModelTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)

    def test_ticket_id_auto_assigned(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='A', last_name='B')
        self.assertIsNotNone(guest.ticket_id)

    def test_ticket_ids_unique(self):
        g1 = Guest.objects.create(reservation=self.reservation, first_name='A', last_name='B')
        g2 = Guest.objects.create(reservation=self.reservation, first_name='C', last_name='D')
        self.assertNotEqual(g1.ticket_id, g2.ticket_id)

    def test_ticket_id_can_be_null(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='Old', last_name='Guest')
        guest.ticket_id = None
        guest.save()
        guest.refresh_from_db()
        self.assertIsNone(guest.ticket_id)

    def test_checked_in_defaults_false(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='A', last_name='B')
        self.assertFalse(guest.checked_in)

    def test_str_contains_name(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='Alice', last_name='Smith')
        self.assertIn('Alice', str(guest))
        self.assertIn('Smith', str(guest))

    def test_deleting_reservation_cascades_to_guests(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='A', last_name='B')
        guest_id = guest.pk
        self.reservation.delete()
        self.assertFalse(Guest.objects.filter(pk=guest_id).exists())


# ---------------------------------------------------------------------------
# ReservationPayment model
# ---------------------------------------------------------------------------

class ReservationPaymentModelTest(TestCase):
    def setUp(self):
        self.show = make_show(
            base_ticket_price=20,
            min_ticket_price=10,
            max_ticket_price=30,
        )
        self.event = make_event(self.show)
        self.reservation = make_reservation(self.event)

    def test_from_reservation_sets_fields(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.reservation, self.reservation)
        self.assertEqual(payment.billing_email, 'test@example.com')
        self.assertEqual(payment.currency, 'EUR')

    def test_ticket_price_uses_custom_when_set(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 25
        self.assertEqual(payment.ticket_price, 25)

    def test_ticket_price_is_decimal_when_custom_set(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 25
        self.assertIsInstance(payment.ticket_price, Decimal)

    def test_ticket_price_uses_show_price(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.ticket_price, 20)

    def test_ticket_price_defaults_to_15_when_no_show_price(self):
        self.show.base_ticket_price = None
        self.show.save()
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.ticket_price, Decimal('15.0'))

    def test_ticket_price_uses_reservation_price_fallback(self):
        self.show.base_ticket_price = None
        self.show.reservation_price = 8
        self.show.save()
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.ticket_price, 8)

    def test_validate_custom_price_within_range(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 15
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_at_min(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 10
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_at_max(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 30
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_below_min_fails(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 5
        self.assertFalse(payment.validate_custom_price(20))

    def test_validate_custom_price_above_max_fails(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = 35
        self.assertFalse(payment.validate_custom_price(20))

    def test_validate_custom_price_none_passes(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = None
        self.assertTrue(payment.validate_custom_price(20))

    def test_total_calculated_from_ticket_count(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        # 1 ticket * 20 EUR
        self.assertEqual(payment.total, 20)

    def test_total_with_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name='G', last_name='H')
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        # 2 tickets * 20 EUR
        self.assertEqual(payment.total, 40)

    def test_get_metadata_contains_reservation_id(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        metadata = payment.get_metadata()
        self.assertIn('reservation_id', metadata)

    def test_event_display(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.save()
        self.assertIn(str(self.event), payment.event())

    def test_ticket_count_display(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.save()
        self.assertEqual(payment.ticket_count(), 1)


# ---------------------------------------------------------------------------
# Send confirmation mail
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendConfirmationMailTest(TestCase):
    def setUp(self):
        from django.core import mail
        self.outbox = mail.outbox

        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event, first_name='Anna', last_name='Doe', email='anna@example.com')

    def test_email_sent_to_reservant(self):
        services.send_confirmation_mail(self.reservation)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn('anna@example.com', self.outbox[0].to)

    def test_email_has_pdf_attachment(self):
        services.send_confirmation_mail(self.reservation)
        email = self.outbox[0]
        self.assertEqual(len(email.attachments), 1)
        filename, content, mimetype = email.attachments[0]
        self.assertEqual(mimetype, 'application/pdf')
        self.assertTrue(content[:4] == b'%PDF')

    def test_pdf_filename_contains_reservation_id(self):
        services.send_confirmation_mail(self.reservation)
        filename, _, _ = self.outbox[0].attachments[0]
        self.assertIn(str(self.reservation.id), filename)

    def test_pdf_one_page_for_solo_reservation(self):
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b'/Type /Page\n'), 1)

    def test_pdf_multi_page_with_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name='B', last_name='C')
        Guest.objects.create(reservation=self.reservation, first_name='D', last_name='E')
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b'/Type /Page\n'), 3)

    def test_guest_with_null_ticket_id_excluded_from_pdf(self):
        guest = Guest.objects.create(reservation=self.reservation, first_name='Old', last_name='Guest')
        guest.ticket_id = None
        guest.save()
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b'/Type /Page\n'), 1)

    def test_email_body_contains_first_name(self):
        services.send_confirmation_mail(self.reservation)
        self.assertIn('Anna', self.outbox[0].body)

    def test_email_body_contains_reservation_id(self):
        services.send_confirmation_mail(self.reservation)
        self.assertIn(str(self.reservation.id), self.outbox[0].body)

    def test_email_includes_payment_info_when_present(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.save()
        services.send_confirmation_mail(self.reservation)
        self.assertIn('EUR', self.outbox[0].body)


# ---------------------------------------------------------------------------
# Purge services
# ---------------------------------------------------------------------------

class PurgeOldPaymentsTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.payment.save()

    def _age_payment(self, days=230):
        ReservationPayment.objects.filter(pk=self.payment.pk).update(
            created=timezone.now() - timedelta(days=days)
        )

    def test_dry_run_returns_counts_without_deleting(self):
        self._age_payment()
        result = services.purge_old_payments(dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['payments_found'], 1)
        self.assertEqual(result['deleted_count'], 0)
        self.assertTrue(ReservationPayment.objects.filter(pk=self.payment.pk).exists())

    def test_deletes_old_payments(self):
        self._age_payment()
        result = services.purge_old_payments(dry_run=False)
        self.assertEqual(result['deleted_count'], 1)
        self.assertFalse(ReservationPayment.objects.filter(pk=self.payment.pk).exists())

    def test_recent_payment_not_deleted(self):
        result = services.purge_old_payments(dry_run=False)
        self.assertEqual(result['deleted_count'], 0)
        self.assertTrue(ReservationPayment.objects.filter(pk=self.payment.pk).exists())


class PurgeOrphanReservationsTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        self.reservation_with_payment = make_reservation(event)
        payment = ReservationPayment.from_reservation(self.reservation_with_payment, variant='paypal')
        payment.save()
        self.orphan = make_reservation(event, email='orphan@example.com')

    def test_dry_run_counts_orphans(self):
        result = services.purge_orphan_reservations(dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['reservations_to_delete'], 1)
        self.assertEqual(result['deleted_reservations'], 0)

    def test_deletes_orphan_reservations(self):
        result = services.purge_orphan_reservations(dry_run=False)
        self.assertEqual(result['deleted_reservations'], 1)
        self.assertFalse(Reservation.objects.filter(pk=self.orphan.pk).exists())
        self.assertTrue(Reservation.objects.filter(pk=self.reservation_with_payment.pk).exists())


# ---------------------------------------------------------------------------
# Reserve view
# ---------------------------------------------------------------------------

class ReserveViewTest(TestCase):
    def setUp(self):
        self.show = make_show()
        self.event = make_event(self.show)

    def _post_data(self, **overrides):
        data = {
            'res-event': self.event.pk,
            'res-attendee_count': 1,
            'res-first_name': 'Anna',
            'res-last_name': 'Doe',
            'res-email': 'anna@example.com',
            'gues-TOTAL_FORMS': 9,
            'gues-INITIAL_FORMS': 0,
            'gues-MIN_NUM_FORMS': 0,
            'gues-MAX_NUM_FORMS': 9,
            'payment-method': 'paypal',
        }
        data.update(overrides)
        return data

    def test_get_renders_form(self):
        response = self.client.get(f'/reserve/{self.show.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('reservation_form', response.context)

    def test_post_valid_creates_reservation(self):
        self.client.post(f'/reserve/{self.show.pk}', self._post_data())
        self.assertEqual(Reservation.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.first_name, 'Anna')
        self.assertEqual(reservation.last_name, 'Doe')
        self.assertEqual(reservation.email, 'anna@example.com')

    def test_post_valid_creates_payment_and_redirects(self):
        response = self.client.post(f'/reserve/{self.show.pk}', self._post_data())
        payment = ReservationPayment.objects.first()
        self.assertIsNotNone(payment)
        self.assertRedirects(response, f'/payment/{payment.pk}', fetch_redirect_response=False)

    def test_post_with_guests_creates_guest_objects(self):
        data = self._post_data(**{
            'res-attendee_count': 3,
            'gues-0-first_name': 'Bob',
            'gues-0-last_name': 'Smith',
            'gues-1-first_name': 'Carol',
            'gues-1-last_name': 'Jones',
        })
        self.client.post(f'/reserve/{self.show.pk}', data)
        self.assertEqual(Guest.objects.count(), 2)

    def test_post_invalid_missing_name_rerenders(self):
        data = self._post_data(**{'res-first_name': '', 'res-last_name': ''})
        response = self.client.post(f'/reserve/{self.show.pk}', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_invalid_custom_price_creates_no_db_records(self):
        # Price below minimum must not leave orphaned reservation+guests in the DB.
        data = self._post_data(**{
            'res-attendee_count': 2,
            'gues-0-first_name': 'Bob',
            'gues-0-last_name': 'Smith',
            'custom-price': '1',  # below effective minimum (max(5, 15-10)=5)
        })
        response = self.client.post(f'/reserve/{self.show.pk}', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertEqual(Guest.objects.count(), 0)
        self.assertEqual(ReservationPayment.objects.count(), 0)

    def test_valid_custom_price_with_guests_creates_all_records(self):
        data = self._post_data(**{
            'res-attendee_count': 2,
            'gues-0-first_name': 'Bob',
            'gues-0-last_name': 'Smith',
            'custom-price': '15',  # within range [5, 25]
        })
        self.client.post(f'/reserve/{self.show.pk}', data)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Guest.objects.count(), 1)
        self.assertEqual(ReservationPayment.objects.count(), 1)
        payment = ReservationPayment.objects.first()
        self.assertEqual(payment.custom_ticket_price, 15)
        self.assertEqual(payment.total, 30)  # 2 tickets * 15 EUR

    def test_get_nonexistent_show_returns_404(self):
        response = self.client.get('/reserve/99999')
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Reservation status view
# ---------------------------------------------------------------------------

class ReservationStatusViewTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(reservation, variant='paypal')
        self.payment.save()

    def test_returns_200(self):
        response = self.client.get(f'/reservation_status/{self.payment.pk}')
        self.assertEqual(response.status_code, 200)

    def test_unknown_payment_returns_404(self):
        response = self.client.get(f'/reservation_status/{uuid.uuid4()}')
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Payment views
# ---------------------------------------------------------------------------

class PaymentViewTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(reservation, variant='paypal')
        self.payment.save()

    def test_payment_page_returns_200(self):
        response = self.client.get(f'/payment/{self.payment.pk}')
        self.assertEqual(response.status_code, 200)

    def test_payment_fail_page_returns_200(self):
        response = self.client.get(f'/payment-failure/{self.payment.pk}')
        self.assertEqual(response.status_code, 200)

    def test_unknown_payment_returns_404(self):
        response = self.client.get(f'/payment/{uuid.uuid4()}')
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Payment success view
# ---------------------------------------------------------------------------

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PaymentSuccessViewTest(TestCase):
    def setUp(self):
        from django.core import mail
        self.outbox = mail.outbox
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.payment.save()

    def test_redirects_to_reservation_status(self):
        response = self.client.get(f'/payment-success/{self.payment.pk}')
        self.assertRedirects(
            response, f'/reservation_status/{self.payment.pk}',
            fetch_redirect_response=False
        )

    def test_sends_confirmation_email(self):
        self.payment.change_status(PaymentStatus.CONFIRMED)
        self.client.get(f'/payment-success/{self.payment.pk}')
        self.assertEqual(len(self.outbox), 1)
        self.assertIn('test@example.com', self.outbox[0].to)

    def test_email_not_sent_for_unconfirmed_payment(self):
        response = self.client.get(f'/payment-success/{self.payment.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.outbox), 0)

    def test_email_send_failure_still_redirects(self):
        self.payment.change_status(PaymentStatus.CONFIRMED)
        with patch('events.services.send_confirmation_mail', side_effect=Exception('mail error')):
            response = self.client.get(f'/payment-success/{self.payment.pk}')
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# QR scanner views
# ---------------------------------------------------------------------------

class QrScannerViewTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', password='pass', is_staff=True)

    def test_scanner_page_requires_staff(self):
        response = self.client.get('/qr-scanner/')
        self.assertNotEqual(response.status_code, 200)

    def test_scanner_page_accessible_to_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get('/qr-scanner/')
        self.assertEqual(response.status_code, 200)

    def test_get_events_requires_staff(self):
        response = self.client.get('/qr-scanner/get-events')
        self.assertNotEqual(response.status_code, 200)

    def test_get_events_returns_json(self):
        self.client.force_login(self.staff)
        show = make_show()
        make_event(show)
        response = self.client.get('/qr-scanner/get-events')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn('title', data[0])

    def test_get_events_excludes_past_events(self):
        self.client.force_login(self.staff)
        show = make_show()
        make_event(show, offset_days=-5)
        response = self.client.get('/qr-scanner/get-events')
        self.assertEqual(response.json(), [])


# ---------------------------------------------------------------------------
# Check-in view
# ---------------------------------------------------------------------------

class CheckInViewTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', password='pass', is_staff=True)
        self.client.force_login(self.staff)

        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)
        self.guest = Guest.objects.create(
            reservation=self.reservation, first_name='Guest', last_name='One'
        )

    def _url(self, ticket_id):
        return f'/qr-scanner/{ticket_id}/check-in'

    def test_check_in_by_reservation_id(self):
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.checked_in)

    def test_check_in_by_guest_ticket_id(self):
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.checked_in)

    def test_guest_check_in_does_not_affect_reservation(self):
        self.client.get(self._url(self.guest.ticket_id))
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.checked_in)

    def test_already_checked_in_reservation_returns_400(self):
        self.reservation.checked_in = True
        self.reservation.save()
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 400)
        self.assertIn('already checked in', response.json()['error'])

    def test_already_checked_in_guest_returns_400(self):
        self.guest.checked_in = True
        self.guest.save()
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 400)
        self.assertIn('already checked in', response.json()['error'])

    def test_unknown_uuid_returns_404(self):
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_reservation_check_in_returns_is_group_true(self):
        response = self.client.get(self._url(self.reservation.id))
        self.assertTrue(response.json().get('is_group'))

    def test_response_includes_guest_names(self):
        response = self.client.get(self._url(self.reservation.id))
        names = response.json()['guests']
        self.assertTrue(any('Test' in name for name in names))
