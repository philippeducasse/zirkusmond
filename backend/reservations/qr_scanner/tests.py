import uuid
from datetime import timedelta
from io import BytesIO
from typing import Any

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from payments import PaymentStatus
from PIL import Image

from events.models import Event
from reservations.models import Guest, Reservation, ReservationPayment
from shows.models import Show

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_image() -> SimpleUploadedFile:
    buf = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile("test.jpg", buf.read(), content_type="image/jpeg")


def make_show(**kwargs: Any) -> Show:
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


def make_event(show: Show, offset_days: int = 7, capacity: int = 150) -> Event:
    base = timezone.now() + timedelta(days=offset_days)
    return Event.objects.create(
        show=show,
        admission=base.replace(hour=19, minute=0, second=0, microsecond=0),
        begin=base.replace(hour=20, minute=0, second=0, microsecond=0),
        reservation_capacity=capacity,
        open_for_reservation=True,
    )


def make_reservation(event: Event, **kwargs: Any) -> Reservation:
    defaults = dict(first_name="Test", last_name="User", email="test@example.com")
    defaults.update(kwargs)
    return Reservation.objects.create(event=event, **defaults)


# ---------------------------------------------------------------------------
# QR scanner views
# ---------------------------------------------------------------------------


class QrScannerViewTest(TestCase):
    def setUp(self) -> None:
        self.staff = User.objects.create_user("staff", password="pass", is_staff=True)

    def test_scanner_page_requires_staff(self) -> None:
        response = self.client.get("/qr-scanner/")
        self.assertNotEqual(response.status_code, 200)

    def test_scanner_page_accessible_to_staff(self) -> None:
        self.client.force_login(self.staff)
        response = self.client.get("/qr-scanner/")
        self.assertEqual(response.status_code, 200)

    def test_get_events_requires_staff(self) -> None:
        response = self.client.get("/qr-scanner/get-events")
        self.assertNotEqual(response.status_code, 200)

    def test_get_events_returns_json(self) -> None:
        self.client.force_login(self.staff)
        show = make_show()
        make_event(show)
        response = self.client.get("/qr-scanner/get-events")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn("title", data[0])

    def test_get_events_excludes_past_events(self) -> None:
        self.client.force_login(self.staff)
        show = make_show()
        make_event(show, offset_days=-5)
        response = self.client.get("/qr-scanner/get-events")
        self.assertEqual(response.json(), [])


# ---------------------------------------------------------------------------
# Check-in view
# ---------------------------------------------------------------------------


class CheckInViewTest(TestCase):
    def setUp(self) -> None:
        self.staff = User.objects.create_user("staff", password="pass", is_staff=True)
        self.client.force_login(self.staff)

        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)
        self.guest = Guest.objects.create(
            reservation=self.reservation, first_name="Guest", last_name="One"
        )

    def _url(self, ticket_id: uuid.UUID) -> str:
        return f"/qr-scanner/{ticket_id}/check-in"

    def test_check_in_by_reservation_id(self) -> None:
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.checked_in)

    def test_check_in_by_guest_ticket_id(self) -> None:
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.checked_in)

    def test_guest_check_in_does_not_affect_reservation(self) -> None:
        self.client.get(self._url(self.guest.ticket_id))
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.checked_in)

    def test_already_checked_in_reservation_returns_400(self) -> None:
        self.reservation.checked_in = True
        self.reservation.save()
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 400)
        self.assertIn("already checked in", response.json()["error"])

    def test_already_checked_in_guest_returns_400(self) -> None:
        self.guest.checked_in = True
        self.guest.save()
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 400)
        self.assertIn("already checked in", response.json()["error"])

    def test_unknown_uuid_returns_404(self) -> None:
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_reservation_check_in_returns_is_group_true(self) -> None:
        response = self.client.get(self._url(self.reservation.id))
        self.assertTrue(response.json().get("is_group"))

    def test_response_includes_guest_names(self) -> None:
        response = self.client.get(self._url(self.reservation.id))
        names = response.json()["guests"]
        self.assertTrue(any("Test" in name for name in names))

    def _make_payment(self, status: str) -> ReservationPayment:
        payment = ReservationPayment.from_reservation(self.reservation, variant="stripe")
        payment.save()
        payment.change_status(status)
        return payment

    def test_rejected_payment_blocks_reservation_check_in(self) -> None:
        self._make_payment(PaymentStatus.REJECTED)
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 402)
        self.assertIn("rejected", response.json()["error"].lower())

    def test_rejected_payment_blocks_guest_check_in(self) -> None:
        self._make_payment(PaymentStatus.REJECTED)
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 402)
        self.assertIn("rejected", response.json()["error"].lower())

    def test_rejected_payment_does_not_mark_checked_in(self) -> None:
        self._make_payment(PaymentStatus.REJECTED)
        self.client.get(self._url(self.reservation.id))
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.checked_in)

    def test_confirmed_payment_allows_check_in(self) -> None:
        self._make_payment(PaymentStatus.CONFIRMED)
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_no_payment_allows_check_in(self) -> None:
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
