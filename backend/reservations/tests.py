from datetime import timedelta
from io import BytesIO
from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from events.models import Event
from newsletter.models import NewsletterRegistration
from reservations.models import Guest, Reservation
from shows.models import Show

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_image() -> SimpleUploadedFile:
    buf = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile("test.jpg", buf.read(), content_type="image/jpeg")


def make_banner_image() -> SimpleUploadedFile:
    buf = BytesIO()
    Image.new("RGB", (400, 225), color="blue").save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile("banner.jpg", buf.read(), content_type="image/jpeg")


def make_show(**kwargs: Any) -> Show:
    defaults = dict(
        title="Test Show",
        description="",
        cast="",
        card_image=make_image(),
        banner_image=make_banner_image(),
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
# Reservation model
# ---------------------------------------------------------------------------


class ReservationModelTest(TestCase):
    def setUp(self) -> None:
        self.show = make_show()
        self.event = make_event(self.show)
        self.reservation = make_reservation(self.event)

    def test_ticket_count_no_guests(self) -> None:
        self.assertEqual(self.reservation.ticket_count(), 1)

    def test_ticket_count_with_guests(self) -> None:
        Guest.objects.create(reservation=self.reservation, first_name="G", last_name="H")
        Guest.objects.create(reservation=self.reservation, first_name="I", last_name="J")
        self.assertEqual(self.reservation.ticket_count(), 3)

    def test_str_contains_event_and_name(self) -> None:
        result = str(self.reservation)
        self.assertIn("User", result)
        self.assertIn("Test", result)

    def test_guests_relation(self) -> None:
        guest = Guest.objects.create(reservation=self.reservation, first_name="G", last_name="H")
        self.assertIn(guest, self.reservation.guests.all())

    def test_checked_in_defaults_false(self) -> None:
        self.assertFalse(self.reservation.checked_in)

    def test_uuid_primary_key(self) -> None:
        self.assertIsNotNone(self.reservation.id)
        self.assertIsInstance(str(self.reservation.id), str)


# ---------------------------------------------------------------------------
# Guest model
# ---------------------------------------------------------------------------


class GuestModelTest(TestCase):
    def setUp(self) -> None:
        show = make_show()
        event = make_event(show)
        self.reservation = make_reservation(event)

    def test_ticket_id_auto_assigned(self) -> None:
        guest = Guest.objects.create(reservation=self.reservation, first_name="A", last_name="B")
        self.assertIsNotNone(guest.ticket_id)

    def test_ticket_ids_unique(self) -> None:
        g1 = Guest.objects.create(reservation=self.reservation, first_name="A", last_name="B")
        g2 = Guest.objects.create(reservation=self.reservation, first_name="C", last_name="D")
        self.assertNotEqual(g1.ticket_id, g2.ticket_id)

    def test_ticket_id_can_be_null(self) -> None:
        guest = Guest.objects.create(
            reservation=self.reservation, first_name="Old", last_name="Guest"
        )
        guest.ticket_id = None
        guest.save()
        guest.refresh_from_db()
        self.assertIsNone(guest.ticket_id)

    def test_checked_in_defaults_false(self) -> None:
        guest = Guest.objects.create(reservation=self.reservation, first_name="A", last_name="B")
        self.assertFalse(guest.checked_in)

    def test_str_contains_name(self) -> None:
        guest = Guest.objects.create(
            reservation=self.reservation, first_name="Alice", last_name="Smith"
        )
        self.assertIn("Alice", str(guest))
        self.assertIn("Smith", str(guest))

    def test_deleting_reservation_cascades_to_guests(self) -> None:
        guest = Guest.objects.create(reservation=self.reservation, first_name="A", last_name="B")
        guest_id = guest.pk
        self.reservation.delete()
        self.assertFalse(Guest.objects.filter(pk=guest_id).exists())


# ---------------------------------------------------------------------------
# Reserve API view
# ---------------------------------------------------------------------------


class ReserveAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.show = make_show()
        self.event = make_event(self.show)

    def _url(self, show_id: int | None = None) -> str:
        pk = show_id if show_id is not None else self.show.pk
        return f"/reservation/{pk}"

    def _post_data(self, **overrides: Any) -> dict[str, Any]:
        data = {
            "event_id": self.event.pk,
            "first_name": "Anna",
            "last_name": "Doe",
            "email": "anna@example.com",
            "attendee_count": 1,
            "payment_method": "paypal",
        }
        data.update(overrides)
        return data

    # -----------------------------------------------------------------------
    # Successful reservation — no guests, no newsletter
    # -----------------------------------------------------------------------

    def test_valid_post_returns_201(self) -> None:
        response = self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(response.status_code, 201)

    def test_valid_post_creates_reservation_and_payment(self) -> None:
        self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(Reservation.objects.count(), 1)

    def test_valid_post_response_contains_reservation_id(self) -> None:
        response = self.client.post(self._url(), self._post_data(), format="json")
        reservation = Reservation.objects.first()
        self.assertIn("reservation_id", response.data)
        self.assertEqual(str(response.data["reservation_id"]), str(reservation.id))

    def test_valid_post_does_not_create_guests(self) -> None:
        self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(Guest.objects.count(), 0)

    # -----------------------------------------------------------------------
    # Reservation with guests
    # -----------------------------------------------------------------------

    def test_post_with_guests_creates_guest_records(self) -> None:
        data = self._post_data(
            attendee_count=3,
            guests=[
                {"first_name": "Bob", "last_name": "Smith"},
                {"first_name": "Carol", "last_name": "Jones"},
            ],
        )
        self.client.post(self._url(), data, format="json")
        self.assertEqual(Guest.objects.count(), 2)

    def test_post_with_guests_links_guests_to_reservation(self) -> None:
        data = self._post_data(
            attendee_count=2,
            guests=[{"first_name": "Bob", "last_name": "Smith"}],
        )
        self.client.post(self._url(), data, format="json")
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.guests.count(), 1)

    # -----------------------------------------------------------------------
    # Newsletter opt-in
    # -----------------------------------------------------------------------

    def test_newsletter_flag_true_registers_email(self) -> None:
        self.client.post(self._url(), self._post_data(newsletter=True), format="json")
        self.assertTrue(
            NewsletterRegistration.objects.filter(email="anna@example.com").exists(),
            "Expected a NewsletterRegistration record for the submitted email.",
        )

    def test_newsletter_flag_false_does_not_register_email(self) -> None:
        self.client.post(self._url(), self._post_data(newsletter=False), format="json")
        self.assertEqual(NewsletterRegistration.objects.count(), 0)

    def test_newsletter_flag_absent_does_not_register_email(self) -> None:
        # newsletter defaults to False; omitting it must not create a record.
        self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(NewsletterRegistration.objects.count(), 0)

    # -----------------------------------------------------------------------
    # Serializer validation failures — expected 400
    # -----------------------------------------------------------------------

    def test_missing_required_fields_returns_400(self) -> None:
        response = self.client.post(self._url(), {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_missing_first_name_returns_400(self) -> None:
        data = self._post_data()
        del data["first_name"]
        response = self.client.post(self._url(), data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_missing_email_returns_400(self) -> None:
        data = self._post_data()
        del data["email"]
        response = self.client.post(self._url(), data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_missing_payment_method_returns_400(self) -> None:
        data = self._post_data()
        del data["payment_method"]
        response = self.client.post(self._url(), data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_serializer_data_creates_no_db_records(self) -> None:
        self.client.post(self._url(), {}, format="json")
        self.assertEqual(Reservation.objects.count(), 0)

    # -----------------------------------------------------------------------
    # Closed event — expected 400
    # -----------------------------------------------------------------------

    def test_closed_event_returns_400(self) -> None:
        self.event.open_for_reservation = False
        self.event.save()
        response = self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(response.status_code, 400)

    def test_closed_event_returns_error_key(self) -> None:
        self.event.open_for_reservation = False
        self.event.save()
        response = self.client.post(self._url(), self._post_data(), format="json")
        self.assertIn("error", response.data)

    def test_closed_event_creates_no_db_records(self) -> None:
        self.event.open_for_reservation = False
        self.event.save()
        self.client.post(self._url(), self._post_data(), format="json")
        self.assertEqual(Reservation.objects.count(), 0)

    # -----------------------------------------------------------------------
    # Custom price validation
    # -----------------------------------------------------------------------
    # make_show() sets base_ticket_price=15; effective range is [5, 25]
    # (max(5, 15-10) to 15+10).

    def test_invalid_custom_price_below_minimum_returns_400(self) -> None:
        # Price 1 is below the minimum of 5.
        response = self.client.post(self._url(), self._post_data(custom_price=1), format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_custom_price_above_maximum_returns_400(self) -> None:
        # Price 99 is above the maximum of 25.
        response = self.client.post(self._url(), self._post_data(custom_price=99), format="json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_custom_price_returns_error_key(self) -> None:
        response = self.client.post(self._url(), self._post_data(custom_price=1), format="json")
        self.assertIn("error", response.data)

    def test_invalid_custom_price_creates_no_db_records(self) -> None:
        self.client.post(self._url(), self._post_data(custom_price=1), format="json")
        self.assertEqual(Reservation.objects.count(), 0)

    def test_valid_custom_price_returns_201(self) -> None:
        response = self.client.post(self._url(), self._post_data(custom_price=20), format="json")
        self.assertEqual(response.status_code, 201)

    # -----------------------------------------------------------------------
    # 404 cases
    # -----------------------------------------------------------------------

    def test_nonexistent_show_returns_404(self) -> None:
        response = self.client.post(self._url(show_id=99999), self._post_data(), format="json")
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_event_returns_404(self) -> None:
        # event_id 99999 does not exist in the database.
        data = self._post_data(event_id=99999)
        response = self.client.post(self._url(), data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_event_belonging_to_different_show_returns_404(self) -> None:
        # An event that exists but belongs to a different show must not be
        # accessible through this show's URL.
        other_show = make_show()
        other_event = make_event(other_show)
        data = self._post_data(event_id=other_event.pk)
        response = self.client.post(self._url(), data, format="json")
        self.assertEqual(response.status_code, 404)
