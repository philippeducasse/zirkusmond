from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.utils import timezone
from payments import PaymentStatus
from PIL import Image

from events.forms import ReservationForm
from events.models import Event
from reservations.models import Reservation, ReservationPayment
from shows.models import Show

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_image():
    buf = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile("test.jpg", buf.read(), content_type="image/jpeg")


def make_show(**kwargs):
    defaults = dict(
        title="Test Show",
        description="",
        cast="",
        card_image=make_image(),
        private=False,
        base_ticket_price=15,
    )
    defaults.update(kwargs)
    return Show.objects.create(**defaults)


def make_event(show, offset_days=7, capacity=150, open_for_reservation=True):
    base = timezone.now() + timedelta(days=offset_days)
    return Event.objects.create(
        show=show,
        admission=base.replace(hour=19, minute=0, second=0, microsecond=0),
        begin=base.replace(hour=20, minute=0, second=0, microsecond=0),
        reservation_capacity=capacity,
        open_for_reservation=open_for_reservation,
    )


def make_reservation(event, **kwargs):
    defaults = dict(first_name="Test", last_name="User", email="test@example.com")
    defaults.update(kwargs)
    return Reservation.objects.create(event=event, **defaults)


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------


class EventModelTest(TestCase):
    def setUp(self):
        self.show = make_show()
        self.event = make_event(self.show)

    def test_str_contains_date(self):
        self.assertIn(".", str(self.event))

    def test_time_and_date(self):
        self.assertRegex(self.event.time_and_date(), r"\d{2}\.\d{2}\.\d{2} at \d{2}:\d{2}")

    def test_date_str(self):
        self.assertRegex(self.event.date_str(), r"\d{2}\.\d{2}\.\d{2}")

    def test_admission_time(self):
        self.assertRegex(self.event.admission_time(), r"\d{2}:\d{2}")

    def test_begin_time(self):
        self.assertRegex(self.event.begin_time(), r"\d{2}:\d{2}")

    def test_elaborate_date_str(self):
        result = self.event.elaborate_date_str()
        self.assertIn(".", result)

    def test_reservation_open_for_future_event(self):
        self.assertTrue(self.event.reservation_open())

    def test_reservation_closed_for_past_event(self):
        past = make_event(self.show, offset_days=-1)
        self.assertFalse(past.reservation_open())

    def test_reservation_closed_when_manually_closed(self):
        closed = make_event(self.show, open_for_reservation=False)
        self.assertFalse(closed.reservation_open())

    def test_reservation_closed_when_over_capacity(self):
        event = make_event(self.show, capacity=1)
        p1 = ReservationPayment.from_reservation(make_reservation(event), variant="paypal")
        p1.save()
        p1.change_status(PaymentStatus.CONFIRMED)
        p2 = ReservationPayment.from_reservation(
            make_reservation(event, email="other@example.com"), variant="paypal"
        )
        p2.save()
        p2.change_status(PaymentStatus.CONFIRMED)
        self.assertFalse(event.reservation_open())

    def test_reservation_count_empty(self):
        self.assertEqual(self.event.reservation_count(), 0)

    def test_reservation_count_with_payment(self):
        reservation = make_reservation(self.event)
        payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        payment.save()
        payment.change_status(PaymentStatus.CONFIRMED)
        self.assertEqual(self.event.reservation_count(), 1)

    def test_reservation_count_unconfirmed_not_counted(self):
        reservation = make_reservation(self.event)
        ReservationPayment.from_reservation(reservation, variant="paypal").save()
        self.assertEqual(self.event.reservation_count(), 0)

    def test_reservation_count_includes_guests(self):
        from reservations.models import Guest

        reservation = make_reservation(self.event)
        payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        payment.save()
        payment.change_status(PaymentStatus.CONFIRMED)
        Guest.objects.create(reservation=reservation, first_name="G", last_name="H")
        self.assertEqual(self.event.reservation_count(), 2)

    def test_reserved_tickets_display_format(self):
        reservation = make_reservation(self.event)
        payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        payment.save()
        payment.change_status(PaymentStatus.CONFIRMED)
        self.assertEqual(self.event.reserved_tickets(), "1/150")

    def test_clean_raises_if_begin_before_admission(self):
        base = timezone.now() + timedelta(days=3)
        event = Event(
            show=self.show,
            admission=base + timedelta(hours=1),
            begin=base,
            reservation_capacity=100,
        )
        with self.assertRaises(ValidationError):
            event.clean()


# ---------------------------------------------------------------------------
# Show price validation
# ---------------------------------------------------------------------------


class ShowPriceValidationTest(TestCase):
    def setUp(self):
        self.show_data = dict(
            title="Test Show",
            description="A description",
            cast="A cast",
            card_image=make_image(),
            private=False,
        )

    def test_valid_price_config_passes(self):
        show = Show(
            **self.show_data, base_ticket_price=20, min_ticket_price=10, max_ticket_price=30
        )
        show.full_clean()

    def test_negative_ticket_price_raises(self):
        show = Show(**self.show_data, base_ticket_price=-10)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("base_ticket_price", ctx.exception.message_dict)

    def test_negative_min_ticket_price_raises(self):
        show = Show(**self.show_data, base_ticket_price=20, min_ticket_price=-5)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("min_ticket_price", ctx.exception.message_dict)

    def test_negative_max_ticket_price_raises(self):
        show = Show(**self.show_data, base_ticket_price=20, max_ticket_price=-5)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("max_ticket_price", ctx.exception.message_dict)

    def test_negative_reservation_price_raises(self):
        show = Show(**self.show_data, reservation_price=-5)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("reservation_price", ctx.exception.message_dict)

    def test_min_above_ticket_price_raises(self):
        show = Show(**self.show_data, base_ticket_price=15, min_ticket_price=20)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("min_ticket_price", ctx.exception.message_dict)

    def test_max_below_ticket_price_raises(self):
        show = Show(**self.show_data, base_ticket_price=20, max_ticket_price=15)
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn("max_ticket_price", ctx.exception.message_dict)

    def test_min_equals_ticket_price_is_valid(self):
        show = Show(**self.show_data, base_ticket_price=20, min_ticket_price=20)
        show.full_clean()

    def test_max_equals_ticket_price_is_valid(self):
        show = Show(**self.show_data, base_ticket_price=20, max_ticket_price=20)
        show.full_clean()

    def test_effective_min_price_uses_custom_value(self):
        show = Show(**self.show_data, base_ticket_price=20, min_ticket_price=12)
        self.assertEqual(show.get_effective_min_price(20), 12)

    def test_effective_min_price_defaults_to_base_minus_10(self):
        show = Show(**self.show_data, base_ticket_price=20)
        self.assertEqual(show.get_effective_min_price(20), 10)

    def test_effective_min_price_floors_at_5(self):
        show = Show(**self.show_data, base_ticket_price=8)
        self.assertEqual(show.get_effective_min_price(8), 5)

    def test_effective_max_price_uses_custom_value(self):
        show = Show(**self.show_data, base_ticket_price=20, max_ticket_price=35)
        self.assertEqual(show.get_effective_max_price(20), 35)

    def test_effective_max_price_defaults_to_base_plus_10(self):
        show = Show(**self.show_data, base_ticket_price=20)
        self.assertEqual(show.get_effective_max_price(20), 30)


# ---------------------------------------------------------------------------
# Reservation form
# ---------------------------------------------------------------------------


class ReservationFormTest(TestCase):
    def setUp(self):
        self.show = make_show()
        self.future = timezone.now() + timedelta(days=7)
        self.past = timezone.now() - timedelta(days=1)

    def _make_event(self, begin, open_for_reservation=True, capacity=150):
        return Event.objects.create(
            show=self.show,
            admission=begin - timedelta(hours=1),
            begin=begin,
            reservation_capacity=capacity,
            open_for_reservation=open_for_reservation,
        )

    def test_future_open_event_included(self):
        event = self._make_event(self.future)
        form = ReservationForm(self.show)
        self.assertIn(event, form.fields["event"].queryset)

    def test_past_event_excluded(self):
        event = self._make_event(self.past)
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields["event"].queryset)

    def test_manually_closed_event_excluded(self):
        event = self._make_event(self.future, open_for_reservation=False)
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields["event"].queryset)

    def test_over_capacity_event_excluded(self):
        event = self._make_event(self.future, capacity=1)
        for r in [make_reservation(event), make_reservation(event, email="other@example.com")]:
            p = ReservationPayment.from_reservation(r, variant="paypal")
            p.save()
            p.change_status(PaymentStatus.CONFIRMED)
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields["event"].queryset)

    def test_open_and_closed_events_filtered_correctly(self):
        open_event = self._make_event(self.future)
        past_event = self._make_event(self.past)
        closed_event = self._make_event(self.future, open_for_reservation=False)
        qs = ReservationForm(self.show).fields["event"].queryset
        self.assertIn(open_event, qs)
        self.assertNotIn(past_event, qs)
        self.assertNotIn(closed_event, qs)

    def test_valid_form_with_all_fields(self):
        event = self._make_event(self.future)
        form = ReservationForm(
            self.show,
            data={
                "event": event.pk,
                "attendee_count": 2,
                "first_name": "Anna",
                "last_name": "Smith",
                "email": "anna@example.com",
            },
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_fields_invalid(self):
        form = ReservationForm(self.show, data={})
        self.assertFalse(form.is_valid())


# ---------------------------------------------------------------------------
# Purge admin view
# ---------------------------------------------------------------------------


class PurgeOldPaymentsViewTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass", is_staff=True)

    def test_get_requires_staff(self):
        response = self.client.get("/mondmin/reservations/reservationpayment/purge-old-payments/")
        self.assertNotEqual(response.status_code, 200)

    def test_get_returns_200_for_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get("/mondmin/reservations/reservationpayment/purge-old-payments/")
        self.assertEqual(response.status_code, 200)

    def test_post_dry_run_redirects(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/mondmin/reservations/reservationpayment/purge-old-payments/", {"dry_run": True, "confirmed_only": False}
        )
        self.assertEqual(response.status_code, 302)

    def test_post_live_run_redirects(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/mondmin/reservations/reservationpayment/purge-old-payments/", {"dry_run": False, "confirmed_only": False}
        )
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# EventAdmin revenue annotation and display
# ---------------------------------------------------------------------------


class EventAdminRevenueTest(TestCase):
    def setUp(self):
        from events.admin import EventAdmin

        self.show = make_show(base_ticket_price=15)
        self.event = make_event(self.show)
        self.user = User.objects.create_superuser("admin", "admin@example.com", "password")
        self.site = AdminSite()
        self.admin = EventAdmin(Event, self.site)
        self.factory = RequestFactory()

    def _get_annotated_event(self):
        request = self.factory.get("/")
        request.user = self.user
        return self.admin.get_queryset(request).get(pk=self.event.pk)

    def _make_payment(self, reservation, total, status=PaymentStatus.CONFIRMED):
        payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        payment.total = total
        payment.status = status
        payment.save()
        return payment

    def test_revenue_display_returns_dash_when_no_payments(self):
        event = self._get_annotated_event()
        self.assertIsNone(event.total_revenue)
        self.assertEqual(self.admin.revenue(event), "—")

    def test_revenue_display_returns_formatted_euro_amount(self):
        reservation = make_reservation(self.event)
        self._make_payment(reservation, Decimal("30.00"))
        event = self._get_annotated_event()
        self.assertEqual(self.admin.revenue(event), "€ 30.00")

    def test_total_revenue_sums_multiple_confirmed_payments(self):
        for i, amount in enumerate([Decimal("15.00"), Decimal("30.00"), Decimal("45.00")]):
            reservation = make_reservation(self.event, email=f"p{i}@example.com")
            self._make_payment(reservation, amount)
        event = self._get_annotated_event()
        self.assertEqual(event.total_revenue, Decimal("90.00"))
        self.assertEqual(self.admin.revenue(event), "€ 90.00")

    def test_total_revenue_excludes_non_confirmed_payments(self):
        reservation = make_reservation(self.event)
        self._make_payment(reservation, Decimal("50.00"), status=PaymentStatus.WAITING)
        event = self._get_annotated_event()
        self.assertIsNone(event.total_revenue)
        self.assertEqual(self.admin.revenue(event), "—")

    def test_total_revenue_only_counts_confirmed_among_mixed_statuses(self):
        reservation = make_reservation(self.event)
        self._make_payment(reservation, Decimal("20.00"), status=PaymentStatus.CONFIRMED)
        reservation2 = make_reservation(self.event, email="b@example.com")
        self._make_payment(reservation2, Decimal("100.00"), status=PaymentStatus.WAITING)
        event = self._get_annotated_event()
        self.assertEqual(event.total_revenue, Decimal("20.00"))


# ---------------------------------------------------------------------------
# ReservationPaymentAdmin confirmed_total display
# ---------------------------------------------------------------------------


class ReservationPaymentAdminConfirmedTotalTest(TestCase):
    def setUp(self):
        from reservations.payments.admin import ReservationPaymentAdmin

        self.show = make_show(base_ticket_price=15)
        self.event = make_event(self.show)
        self.reservation = make_reservation(self.event)
        self.site = AdminSite()
        self.admin = ReservationPaymentAdmin(ReservationPayment, self.site)

    def _make_payment(self, total, status):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.total = total
        payment.status = status
        payment.save()
        return payment

    def test_confirmed_total_shows_amount_for_confirmed_payment(self):
        payment = self._make_payment(Decimal("30.00"), PaymentStatus.CONFIRMED)
        self.assertEqual(self.admin.confirmed_total(payment), "€ 30.00")

    def test_confirmed_total_shows_zero_for_waiting_payment(self):
        payment = self._make_payment(Decimal("30.00"), PaymentStatus.WAITING)
        self.assertEqual(self.admin.confirmed_total(payment), "€ 0.00")

    def test_confirmed_total_shows_zero_for_rejected_payment(self):
        payment = self._make_payment(Decimal("30.00"), PaymentStatus.REJECTED)
        self.assertEqual(self.admin.confirmed_total(payment), "€ 0.00")

    def test_confirmed_total_shows_zero_for_refunded_payment(self):
        payment = self._make_payment(Decimal("30.00"), PaymentStatus.REFUNDED)
        self.assertEqual(self.admin.confirmed_total(payment), "€ 0.00")
