from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Any

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandParser
from payments import PaymentStatus
from PIL import Image

from events.models import Event
from reservations.models import Guest, Reservation, ReservationPayment
from shows.models import Show


class Command(BaseCommand):
    help = "Populate database with fixture shows and events"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing shows and events before creating fixtures",
        )

    def create_placeholder_image(self) -> ContentFile:
        """Create a simple placeholder image."""
        image = Image.new("RGB", (400, 300), color="lightblue")
        image_io = BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)
        return ContentFile(image_io.getvalue(), name="placeholder.png")

    def handle(self, *args: Any, **options: Any) -> None:
        if options["clear"]:
            Show.objects.all().delete()
            Event.objects.all().delete()
            self.stdout.write(self.style.WARNING("Deleted all existing shows and events"))

        # Create 50 shows: 5 with future events (2036), 45 with past events
        shows_to_create: list[tuple[Show, bool]] = []
        for i in range(1, 51):
            is_future = i <= 5
            show = Show(
                title=f"Show {i:02d} - {'Future' if is_future else 'Past'}",
                description=f"<p>Description for show {i}</p>",
                cast=f"<p>Cast for show {i}</p>",
                base_ticket_price=15,
                card_image=self.create_placeholder_image(),
            )
            shows_to_create.append((show, is_future))

        # Save shows first
        shows: list[tuple[Show, bool]] = []
        for show, is_future in shows_to_create:
            show.save()
            shows.append((show, is_future))
            self.stdout.write(f"Created show: {show.title}")

        # Create events for each show with different dates
        events_to_create: list[Event] = []
        for idx, (show, is_future) in enumerate(shows):
            # Each show gets 1-10 events
            num_events = 1 + (idx % 10)

            for event_idx in range(num_events):
                if is_future:
                    # Events in 2036, spread across multiple months
                    month = 6 + ((idx + event_idx) % 7)
                    day = 5 + ((idx + event_idx) % 20)
                    base_date = datetime(2036, month, day, 20, 0, 0, tzinfo=UTC)
                else:
                    # Events in past (spread across 2022-2024), different dates
                    year = 2022 + ((show.id - 6 + event_idx) % 3)
                    month = 1 + ((show.id - 6 + event_idx) % 12)
                    day = 5 + ((idx + event_idx) % 25)
                    base_date = datetime(year, month, day, 20, 0, 0, tzinfo=UTC)

                admission = base_date - timedelta(hours=1)
                event = Event(
                    show=show,
                    admission=admission,
                    begin=base_date,
                    reservation_capacity=300,
                    open_for_reservation=is_future,
                )
                events_to_create.append(event)

        Event.objects.bulk_create(events_to_create)

        # Create reservations and payments for all events
        reservations_to_create: list[Reservation] = []
        payments_to_create: list[ReservationPayment] = []
        guests_to_create: list[Guest] = []

        for event in Event.objects.all():
            # Create 2-8 reservations per event
            num_reservations = 2 + (event.id % 7)
            for res_idx in range(num_reservations):
                reservation = Reservation(
                    event=event,
                    first_name=f"Customer{event.id}_{res_idx}",
                    last_name=f"Name{event.id}",
                    email=f"customer{event.id}_{res_idx}@example.com",
                )
                reservations_to_create.append(reservation)

        Reservation.objects.bulk_create(reservations_to_create)

        # Add guests and create payments
        for reservation in Reservation.objects.filter(event__in=Event.objects.all()):
            # Add 1-3 guests per reservation
            num_guests = reservation.id.int % 3
            for guest_idx in range(num_guests):
                guest = Guest(
                    reservation=reservation,
                    first_name=f"Guest{guest_idx}",
                    last_name=reservation.last_name,
                )
                guests_to_create.append(guest)

            # Create payment with confirmed status
            ticket_count = 1 + num_guests
            price_per_ticket = 15
            total = ticket_count * price_per_ticket

            payment = ReservationPayment(
                reservation=reservation,
                status=PaymentStatus.CONFIRMED,
                total=total,
                billing_email=reservation.email,
                description=f"Reservations for {reservation.event}",
                currency="EUR",
                variant="default",
            )
            payments_to_create.append(payment)

        Guest.objects.bulk_create(guests_to_create)
        ReservationPayment.objects.bulk_create(payments_to_create)

        total_events = len(events_to_create)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created 50 shows with {total_events} events (1-10 per show)\n"
                "  - 5 future shows with events in 2036\n"
                "  - 45 past shows with events in 2022-2024\n"
                "  - Added reservations and payments for revenue tracking"
            )
        )
