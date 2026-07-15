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

# Varying-length HTML texts so the frontend can be tested with short,
# medium and very long show descriptions.
SHOW_DESCRIPTIONS = [
    # very short
    "<p>Ein Abend voller Zirkuszauber.</p>",
    # short
    (
        "<p>Manege frei! Die jungen Artistinnen und Artisten von Zirkus Mond "
        "zeigen ihr neues Programm — akrobatisch, poetisch und ein bisschen verrückt.</p>"
    ),
    # medium
    (
        "<p>Was passiert, wenn der Mond eines Nachts einfach nicht aufgehen will? "
        "In dieser Inszenierung machen sich die Kinder des Zirkus Mond auf die Suche "
        "nach dem verschwundenen Himmelskörper und begegnen dabei jonglierenden "
        "Sternschnuppen, einer schüchternen Wolke und einem sehr eigensinnigen Kometen.</p>"
        "<p>Eine Geschichte über Mut, Freundschaft und die Kunst, auch im Dunkeln "
        "das Gleichgewicht zu halten. Für Zuschauerinnen und Zuschauer ab 5 Jahren.</p>"
    ),
    # long
    (
        "<p>Seit Monaten proben über vierzig Kinder und Jugendliche für diesen Abend: "
        "<strong>Luftakrobatik am Vertikaltuch</strong>, waghalsige Pyramiden, Diabolo, "
        "Einrad und Clownerie verweben sich zu einer Reise durch eine Nacht, in der "
        "nichts so bleibt, wie es scheint.</p>"
        "<p>Die Bühne verwandelt sich vom schlafenden Hinterhof in ein Meer aus "
        "Sternen, während das Live-Orchester der Musikschule die Vorstellung mit "
        "eigens komponierten Stücken begleitet. Zwischen den Nummern führen zwei "
        "streitlustige Nachtwächter durch das Programm — und geraten dabei selbst "
        "immer tiefer in den Sog der Manege.</p>"
        "<p>Die Vorstellung dauert etwa 90 Minuten inklusive Pause. In der Pause gibt "
        "es Getränke und selbstgebackenen Kuchen; der Erlös kommt der Zirkusschule "
        "zugute.</p>"
        "<ul>"
        "<li>Dauer: ca. 90 Minuten mit Pause</li>"
        "<li>Empfohlen ab 5 Jahren</li>"
        "<li>Einlass eine Stunde vor Beginn</li>"
        "</ul>"
    ),
    # very long
    (
        "<p>Es beginnt mit einem Flüstern hinter dem Vorhang. Dann ein Trommelwirbel, "
        "ein Lichtkegel, und plötzlich steht die ganze Manege kopf: <em>Zirkus Mond</em> "
        "lädt zur großen Jahresvorstellung, dem Höhepunkt eines langen Trainingsjahres.</p>"
        "<p>In der ersten Hälfte entführen die jüngsten Gruppen das Publikum in einen "
        "Traum aus Seifenblasen und Bodenakrobatik. Die Mittelstufe übernimmt mit "
        "rasanten Jonglagen, bei denen auch mal eine Keule im Publikum landet — keine "
        "Sorge, das gehört (meistens) so. Kurz vor der Pause zeigt die Trapezgruppe "
        "ihre neue Nummer in sechs Metern Höhe, an der sie seit dem Winter gefeilt hat.</p>"
        "<p>Nach der Pause wird es leiser: Ein Schattenspiel erzählt die Geschichte "
        "eines Mädchens, das dem Mond ein Geheimnis anvertraut. Daraus entspinnt sich "
        "das große Finale, in dem alle Gruppen gemeinsam auf der Bühne stehen — über "
        "sechzig Mitwirkende, ein Feuerwerk aus Farben, Musik und Bewegung.</p>"
        "<p>Der Zirkus Mond ist ein gemeinnütziger Kinder- und Jugendzirkus. Alle "
        "Nummern wurden von den Kindern gemeinsam mit den Trainerinnen und Trainern "
        "entwickelt. Mit dem Kauf einer Karte unterstützen Sie die pädagogische "
        "Arbeit des Vereins.</p>"
        "<p>Bitte beachten Sie: Die Plätze sind nicht nummeriert. Wir empfehlen, "
        "rechtzeitig zu kommen — der Einlass beginnt eine Stunde vor der Vorstellung. "
        "Für Rollstuhlfahrerinnen und Rollstuhlfahrer halten wir Plätze am Rand der "
        "Tribüne frei; bitte geben Sie uns kurz Bescheid.</p>"
    ),
]

SHOW_CASTS = [
    # very short
    "<p>Die Trapezgruppe des Zirkus Mond.</p>",
    # short
    (
        "<p>Es spielen die Akrobatik- und Jonglagegruppen der Mittelstufe, "
        "begleitet von der Zirkuskapelle.</p>"
    ),
    # medium
    (
        "<p><strong>Mitwirkende:</strong></p>"
        "<ul>"
        "<li>Luftartistik: Gruppe Sternschnuppe</li>"
        "<li>Bodenakrobatik: Gruppe Kometenschweif</li>"
        "<li>Clownerie: Jakob, Milla und der große Unbekannte</li>"
        "<li>Musik: Zirkuskapelle Mondlicht</li>"
        "</ul>"
    ),
    # long
    (
        "<p>Über vierzig Kinder und Jugendliche zwischen 6 und 17 Jahren stehen an "
        "diesem Abend in der Manege. Die Nummern haben sie im Laufe des Jahres in "
        "ihren Trainingsgruppen selbst entwickelt.</p>"
        "<p><strong>In der Manege:</strong></p>"
        "<ul>"
        "<li>Vertikaltuch &amp; Trapez: Aylin, Bruno, Charlotte, Damian, Elif</li>"
        "<li>Pyramiden &amp; Partnerakrobatik: die Donnerstagsgruppe</li>"
        "<li>Diabolo &amp; Keulen: Ferdinand, Greta, Hannes</li>"
        "<li>Einrad-Parade: die Einsteiger der Montagsgruppe</li>"
        "<li>Clownsduo: Ida &amp; Jonathan</li>"
        "</ul>"
        "<p><strong>Hinter den Kulissen:</strong> Regie und Training: das Team der "
        "Zirkusschule. Licht und Ton: die Technik-AG. Kostüme: die Eltern-Nähwerkstatt.</p>"
    ),
]


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
                description=SHOW_DESCRIPTIONS[i % len(SHOW_DESCRIPTIONS)],
                cast=SHOW_CASTS[i % len(SHOW_CASTS)],
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
                    start = datetime(2022, 1, 1, 20, 0, 0, tzinfo=UTC)
                    days_offset = ((idx * 37) + (event_idx * 11)) % (3 * 365)
                    base_date = start + timedelta(days=days_offset)

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
