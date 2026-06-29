import json as _json
import uuid
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from payments import PaymentStatus
from PIL import Image

from events import services
from events.models import Event
from reservations.models import Guest, Reservation, ReservationPayment
from reservations.payments.models import Payment
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
    defaults = dict(first_name="Test", last_name="User", email="test@example.com")
    defaults.update(kwargs)
    return Reservation.objects.create(event=event, **defaults)


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
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.reservation, self.reservation)
        self.assertEqual(payment.billing_email, "test@example.com")
        self.assertEqual(payment.currency, "EUR")

    def test_ticket_price_uses_custom_when_set(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 25
        self.assertEqual(payment.ticket_price, 25)

    def test_ticket_price_is_decimal_when_custom_set(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 25
        self.assertIsInstance(payment.ticket_price, Decimal)

    def test_ticket_price_uses_show_price(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.ticket_price, 20)

    def test_ticket_price_defaults_to_15_when_no_show_price(self):
        self.show.base_ticket_price = None
        self.show.save()
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.ticket_price, Decimal("15.0"))

    def test_ticket_price_uses_reservation_price_fallback(self):
        self.show.base_ticket_price = None
        self.show.reservation_price = 8
        self.show.save()
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.ticket_price, 8)

    def test_validate_custom_price_within_range(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 15
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_at_min(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 10
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_at_max(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 30
        self.assertTrue(payment.validate_custom_price(20))

    def test_validate_custom_price_below_min_fails(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 5
        self.assertFalse(payment.validate_custom_price(20))

    def test_validate_custom_price_above_max_fails(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = 35
        self.assertFalse(payment.validate_custom_price(20))

    def test_validate_custom_price_none_passes(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.custom_ticket_price = None
        self.assertTrue(payment.validate_custom_price(20))

    def test_total_calculated_from_ticket_count(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.total, 20)

    def test_total_with_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name="G", last_name="H")
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.assertEqual(payment.total, 40)

    def test_get_metadata_contains_reservation_id(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        metadata = payment.get_metadata()
        self.assertIn("reservation_id", metadata)

    def test_event_display(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.save()
        self.assertIn(str(self.event), payment.event())

    def test_ticket_count_display(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.save()
        self.assertEqual(payment.ticket_count(), 1)


# ---------------------------------------------------------------------------
# Payment model
# ---------------------------------------------------------------------------


class PaymentCreateForReservationTest(TestCase):
    def setUp(self):
        self.show = make_show(base_ticket_price=20, min_ticket_price=10, max_ticket_price=30)
        self.event = make_event(self.show)
        self.reservation = make_reservation(self.event)

    def test_creates_payment_with_valid_price(self):
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=20)
        self.assertIsNotNone(payment.pk)
        self.assertEqual(payment.custom_ticket_price, 20)
        self.assertEqual(payment.reservation, self.reservation)

    def test_total_is_ticket_count_times_price(self):
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=20)
        self.assertEqual(payment.total, Decimal("20"))

    def test_total_includes_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name="G", last_name="H")
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=15)
        self.assertEqual(payment.total, Decimal("30"))

    def test_price_at_minimum_boundary_is_accepted(self):
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=10)
        self.assertEqual(payment.custom_ticket_price, 10)

    def test_price_at_maximum_boundary_is_accepted(self):
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=30)
        self.assertEqual(payment.custom_ticket_price, 30)

    def test_none_price_raises(self):
        with self.assertRaises(ValueError):
            Payment.create_for_reservation(self.reservation, custom_ticket_price=None)

    def test_price_below_minimum_raises(self):
        with self.assertRaises(ValueError):
            Payment.create_for_reservation(self.reservation, custom_ticket_price=9)

    def test_price_above_maximum_raises(self):
        with self.assertRaises(ValueError):
            Payment.create_for_reservation(self.reservation, custom_ticket_price=31)

    def test_status_defaults_to_pending(self):
        payment = Payment.create_for_reservation(self.reservation, custom_ticket_price=20)
        self.assertEqual(payment.status, Payment.Status.PENDING)


# ---------------------------------------------------------------------------
# Send confirmation mail
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendConfirmationMailTest(TestCase):
    def setUp(self):
        from django.core import mail

        self.outbox = mail.outbox

        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(
            event, first_name="Anna", last_name="Doe", email="anna@example.com"
        )

    def test_email_sent_to_reservant(self):
        services.send_confirmation_mail(self.reservation)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("anna@example.com", self.outbox[0].to)

    def test_email_has_pdf_attachment(self):
        services.send_confirmation_mail(self.reservation)
        email = self.outbox[0]
        self.assertEqual(len(email.attachments), 1)
        filename, content, mimetype = email.attachments[0]
        self.assertEqual(mimetype, "application/pdf")
        self.assertTrue(content[:4] == b"%PDF")

    def test_pdf_filename_contains_reservation_id(self):
        services.send_confirmation_mail(self.reservation)
        filename, _, _ = self.outbox[0].attachments[0]
        self.assertIn(str(self.reservation.id), filename)

    def test_pdf_one_page_for_solo_reservation(self):
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b"/Type /Page\n"), 1)

    def test_pdf_multi_page_with_guests(self):
        Guest.objects.create(reservation=self.reservation, first_name="B", last_name="C")
        Guest.objects.create(reservation=self.reservation, first_name="D", last_name="E")
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b"/Type /Page\n"), 3)

    def test_guest_with_null_ticket_id_excluded_from_pdf(self):
        guest = Guest.objects.create(
            reservation=self.reservation, first_name="Old", last_name="Guest"
        )
        guest.ticket_id = None
        guest.save()
        services.send_confirmation_mail(self.reservation)
        _, content, _ = self.outbox[0].attachments[0]
        self.assertEqual(content.count(b"/Type /Page\n"), 1)

    def test_email_body_contains_first_name(self):
        services.send_confirmation_mail(self.reservation)
        self.assertIn("Anna", self.outbox[0].body)

    def test_email_body_contains_reservation_id(self):
        services.send_confirmation_mail(self.reservation)
        self.assertIn(str(self.reservation.id), self.outbox[0].body)

    def test_email_includes_payment_info_when_present(self):
        payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        payment.save()
        services.send_confirmation_mail(self.reservation)
        self.assertIn("EUR", self.outbox[0].body)


# ---------------------------------------------------------------------------
# Purge services
# ---------------------------------------------------------------------------


class PurgeOldPaymentsTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.payment.save()

    def _age_payment(self, days=230):
        ReservationPayment.objects.filter(pk=self.payment.pk).update(
            created=timezone.now() - timedelta(days=days)
        )

    def test_dry_run_returns_counts_without_deleting(self):
        self._age_payment()
        result = services.purge_old_payments(dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["payments_found"], 1)
        self.assertEqual(result["deleted_count"], 0)
        self.assertTrue(ReservationPayment.objects.filter(pk=self.payment.pk).exists())

    def test_deletes_old_payments(self):
        self._age_payment()
        result = services.purge_old_payments(dry_run=False)
        self.assertEqual(result["deleted_count"], 1)
        self.assertFalse(ReservationPayment.objects.filter(pk=self.payment.pk).exists())

    def test_recent_payment_not_deleted(self):
        result = services.purge_old_payments(dry_run=False)
        self.assertEqual(result["deleted_count"], 0)
        self.assertTrue(ReservationPayment.objects.filter(pk=self.payment.pk).exists())


class PurgeOrphanReservationsTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        self.reservation_with_payment = make_reservation(event)
        payment = ReservationPayment.from_reservation(
            self.reservation_with_payment, variant="paypal"
        )
        payment.save()
        self.orphan = make_reservation(event, email="orphan@example.com")

    def test_dry_run_counts_orphans(self):
        result = services.purge_orphan_reservations(dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["reservations_to_delete"], 1)
        self.assertEqual(result["deleted_reservations"], 0)

    def test_deletes_orphan_reservations(self):
        result = services.purge_orphan_reservations(dry_run=False)
        self.assertEqual(result["deleted_reservations"], 1)
        self.assertFalse(Reservation.objects.filter(pk=self.orphan.pk).exists())
        self.assertTrue(Reservation.objects.filter(pk=self.reservation_with_payment.pk).exists())


# ---------------------------------------------------------------------------
# Payment views
# ---------------------------------------------------------------------------


class PaymentViewTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        self.payment.save()

    def test_payment_fail_page_returns_200(self):
        response = self.client.get(f"/payments/{self.payment.pk}/failure")
        self.assertEqual(response.status_code, 200)

    def test_unknown_payment_returns_404(self):
        response = self.client.get(f"/payments/{uuid.uuid4()}")
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Payment success view
# ---------------------------------------------------------------------------


class PaymentSuccessViewTest(TestCase):
    def setUp(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        self.payment = ReservationPayment.from_reservation(reservation, variant="paypal")
        self.payment.save()

    def test_success_page_returns_200(self):
        response = self.client.get(f"/payments/{self.payment.pk}/success")
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# parse_custom_price service
# ---------------------------------------------------------------------------


class ParseCustomPriceTest(TestCase):
    def setUp(self):
        from reservations.payments.services import parse_custom_price

        self.parse = parse_custom_price
        self.show = make_show(base_ticket_price=20, min_ticket_price=10, max_ticket_price=30)

    def test_none_returns_none(self):
        self.assertIsNone(self.parse(self.show, None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(self.parse(self.show, ""))

    def test_unparseable_string_returns_none(self):
        self.assertIsNone(self.parse(self.show, "abc"))

    def test_valid_price_returns_decimal(self):
        self.assertEqual(self.parse(self.show, "20"), Decimal("20"))

    def test_price_at_minimum_is_valid(self):
        self.assertEqual(self.parse(self.show, "10"), Decimal("10"))

    def test_price_at_maximum_is_valid(self):
        self.assertEqual(self.parse(self.show, "30"), Decimal("30"))

    def test_price_below_minimum_raises(self):
        with self.assertRaises(ValueError):
            self.parse(self.show, "1")

    def test_price_above_maximum_raises(self):
        with self.assertRaises(ValueError):
            self.parse(self.show, "99")


# ---------------------------------------------------------------------------
# Payment confirmed signal
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PaymentConfirmedSignalTest(TestCase):
    def setUp(self):
        from django.core import mail

        self.outbox = mail.outbox
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event, email="test@example.com")
        self.payment = ReservationPayment.from_reservation(self.reservation, variant="paypal")
        self.payment.save()

    def test_email_sent_on_confirmed(self):
        self.payment.change_status(PaymentStatus.CONFIRMED)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("test@example.com", self.outbox[0].to)

    def test_email_not_sent_on_waiting(self):
        self.payment.change_status(PaymentStatus.WAITING)
        self.assertEqual(len(self.outbox), 0)

    def test_rejection_email_sent_on_rejected(self):
        self.payment.change_status(PaymentStatus.REJECTED)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("test@example.com", self.outbox[0].to)

    def test_send_failure_does_not_raise(self):
        with patch("events.services.send_confirmation_mail", side_effect=Exception("smtp error")):
            self.payment.change_status(PaymentStatus.CONFIRMED)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)

    def test_payment_without_reservation_does_not_raise(self):
        from reservations.payments.signals import on_payment_status_changed

        self.payment.reservation = None
        on_payment_status_changed(sender=ReservationPayment, instance=self.payment)
        self.assertEqual(len(self.outbox), 0)


# ---------------------------------------------------------------------------
# Payment URL methods
# ---------------------------------------------------------------------------


class PaymentURLTest(TestCase):
    def setUp(self):
        show = make_show(base_ticket_price=20, min_ticket_price=10, max_ticket_price=30)
        event = make_event(show)
        reservation = make_reservation(event)
        self.payment = Payment.objects.create(
            payment_method=Payment.PaymentMethod.CARD,
            reservation=reservation,
            custom_ticket_price=20,
            total=Decimal("20"),
        )

    @override_settings(PAYMENT_USES_SSL=True, PAYMENT_HOST="example.com")
    def test_failure_url_uses_https_when_ssl_enabled(self):
        url = self.payment.get_failure_url()
        self.assertTrue(url.startswith("https://"))
        self.assertIn(str(self.payment.pk), url)
        self.assertIn("failure", url)

    @override_settings(PAYMENT_USES_SSL=False, PAYMENT_HOST="example.com")
    def test_failure_url_uses_http_when_ssl_disabled(self):
        url = self.payment.get_failure_url()
        self.assertTrue(url.startswith("http://"))

    @override_settings(PAYMENT_USES_SSL=True, PAYMENT_HOST="example.com")
    def test_success_url_uses_https_when_ssl_enabled(self):
        url = self.payment.get_success_url()
        self.assertTrue(url.startswith("https://"))
        self.assertIn(str(self.payment.pk), url)
        self.assertIn("success", url)

    @override_settings(PAYMENT_USES_SSL=False, PAYMENT_HOST="example.com")
    def test_success_url_uses_http_when_ssl_disabled(self):
        url = self.payment.get_success_url()
        self.assertTrue(url.startswith("http://"))

    def test_payment_method_card_value(self):
        self.assertEqual(Payment.PaymentMethod.CARD, "card")

    def test_payment_method_paypal_value(self):
        self.assertEqual(Payment.PaymentMethod.PAYPAL, "paypal")


# ---------------------------------------------------------------------------
# Stripe webhook view
# ---------------------------------------------------------------------------

STRIPE_TEST_SETTINGS = {
    "stripe": (
        "reservations.payments.stripe_provider.StripeProviderV3",
        {
            "api_key": "test",
            "endpoint_secret": "",
            "secure_endpoint": False,
        },
    ),
}


@override_settings(PAYMENT_VARIANTS=STRIPE_TEST_SETTINGS)
class StripeWebhookViewTest(TestCase):
    URL = "/payments/process/stripe/"

    def _make_payment(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        payment = ReservationPayment.from_reservation(reservation, variant="stripe")
        payment.save()
        return payment

    def _post_event(self, token, event_type, status="complete", payment_status="paid"):
        body = {
            "type": event_type,
            "data": {
                "object": {
                    "client_reference_id": str(token),
                    "status": status,
                    "payment_status": payment_status,
                }
            },
        }
        return self.client.post(self.URL, data=_json.dumps(body), content_type="application/json")

    def test_completed_paid_session_confirms_payment(self):
        payment = self._make_payment()
        response = self._post_event(payment.token, "checkout.session.completed")
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)

    def test_expired_session_sets_error_status(self):
        payment = self._make_payment()
        response = self._post_event(payment.token, "checkout.session.expired", status="expired")
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.ERROR)

    def test_unknown_event_type_does_not_change_status(self):
        payment = self._make_payment()
        response = self._post_event(payment.token, "payment_intent.created")
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.WAITING)

    def test_unknown_token_returns_404(self):
        response = self._post_event(uuid.uuid4(), "checkout.session.completed")
        self.assertEqual(response.status_code, 404)

    def test_async_payment_succeeded_confirms_payment(self):
        payment = self._make_payment()
        response = self._post_event(
            payment.token, "checkout.session.async_payment_succeeded", payment_status="paid"
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)

    def test_async_payment_failed_rejects_payment(self):
        payment = self._make_payment()
        response = self._post_event(
            payment.token, "checkout.session.async_payment_failed", payment_status="unpaid"
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.REJECTED)

    def test_completed_with_unpaid_status_does_not_confirm(self):
        payment = self._make_payment()
        response = self._post_event(
            payment.token, "checkout.session.completed", payment_status="unpaid"
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.WAITING)

    def test_already_confirmed_payment_stays_confirmed(self):
        payment = self._make_payment()
        payment.change_status(PaymentStatus.CONFIRMED)
        response = self._post_event(payment.token, "checkout.session.completed")
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)

    def test_rejected_payment_updated_to_confirmed_by_completed_webhook(self):
        """Webhook updates payment status, so rejected can become confirmed if webhook says so"""
        payment = self._make_payment()
        payment.change_status(PaymentStatus.REJECTED)
        response = self._post_event(payment.token, "checkout.session.completed")
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)

    def test_missing_client_reference_id_raises_error(self):
        from payments import PaymentError

        body = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "status": "complete",
                    "payment_status": "paid",
                }
            },
        }
        with self.assertRaises(PaymentError):
            self.client.post(self.URL, data=_json.dumps(body), content_type="application/json")

    def test_missing_object_raises_error(self):
        from payments import PaymentError

        body = {"type": "checkout.session.completed", "data": {}}
        with self.assertRaises(PaymentError):
            self.client.post(self.URL, data=_json.dumps(body), content_type="application/json")

    def test_invalid_json_raises_error(self):
        import json

        with self.assertRaises(json.JSONDecodeError):
            self.client.post(self.URL, data="invalid json", content_type="application/json")


# ---------------------------------------------------------------------------
# Stripe payment rejection/failure emails
# ---------------------------------------------------------------------------


@override_settings(PAYMENT_VARIANTS=STRIPE_TEST_SETTINGS)
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StripePaymentRejectionEmailTest(TestCase):
    URL = "/payments/process/stripe/"

    def setUp(self):
        from django.core import mail

        self.outbox = mail.outbox

    def _make_payment(self):
        show = make_show()
        event = make_event(show)
        reservation = make_reservation(event)
        payment = ReservationPayment.from_reservation(reservation, variant="stripe")
        payment.save()
        return payment

    def _post_event(self, token, event_type, status="complete", payment_status="paid"):
        body = {
            "type": event_type,
            "data": {
                "object": {
                    "client_reference_id": str(token),
                    "status": status,
                    "payment_status": payment_status,
                }
            },
        }
        return self.client.post(self.URL, data=_json.dumps(body), content_type="application/json")

    def test_rejected_payment_sends_failure_email(self):
        payment = self._make_payment()
        response = self._post_event(
            payment.token,
            "checkout.session.async_payment_failed",
            status="requires_payment_method",
            payment_status="unpaid",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("Failed", self.outbox[0].subject)
        self.assertIn(payment.reservation.email, self.outbox[0].to)

    def test_confirmed_payment_sends_confirmation_email(self):
        payment = self._make_payment()
        response = self._post_event(payment.token, "checkout.session.completed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("thank you", self.outbox[0].subject.lower())
        self.assertIn(payment.reservation.email, self.outbox[0].to)

    def test_rejection_email_includes_order_id(self):
        payment = self._make_payment()
        self._post_event(
            payment.token,
            "checkout.session.async_payment_failed",
            status="requires_payment_method",
            payment_status="unpaid",
        )
        self.assertEqual(len(self.outbox), 1)
        self.assertIn(str(payment.pk), self.outbox[0].body)

    def test_rejection_email_includes_event_info(self):
        payment = self._make_payment()
        self._post_event(
            payment.token,
            "checkout.session.async_payment_failed",
            status="requires_payment_method",
            payment_status="unpaid",
        )
        self.assertEqual(len(self.outbox), 1)
        self.assertIn(payment.reservation.event.show.title, self.outbox[0].body)

    def test_expired_session_does_not_send_email(self):
        payment = self._make_payment()
        self._post_event(payment.token, "checkout.session.expired", status="expired")
        self.assertEqual(len(self.outbox), 0)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.ERROR)

    def test_charge_failed_sends_rejection_email(self):
        payment = self._make_payment()
        payment.attrs.session = {"payment_intent": "pi_test_charge_abc123"}
        payment.save()
        body = {
            "type": "charge.failed",
            "data": {
                "object": {
                    "id": "ch_test_abc123",
                    "payment_intent": "pi_test_charge_abc123",
                    "status": "failed",
                }
            },
        }
        response = self.client.post(
            self.URL, data=_json.dumps(body), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("Failed", self.outbox[0].subject)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.REJECTED)

    def test_payment_intent_payment_failed_sends_rejection_email(self):
        payment = self._make_payment()
        payment.attrs.session = {"payment_intent": "pi_test_pi_failed_xyz789"}
        payment.save()
        body = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {"id": "pi_test_pi_failed_xyz789", "status": "requires_payment_method"}
            },
        }
        response = self.client.post(
            self.URL, data=_json.dumps(body), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.outbox), 1)
        self.assertIn("Failed", self.outbox[0].subject)
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.REJECTED)
