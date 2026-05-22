import datetime
import json
import logging
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Exists, F, OuterRef
from django.utils import timezone
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from .models import Guest, Person, Reservation, ReservationPayment
from stats.models import SiteStats
from payments import PaymentStatus

logger = logging.getLogger(__name__)

HALF_YEAR_DAYS = 220  # ≈6 months


# ---------------------------------------------------------------------------
# Confirmation email
# ---------------------------------------------------------------------------

def _make_qr_buffer(data: dict) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    buf = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buf, format='PNG')
    buf.seek(0)
    return buf


def _build_tickets_pdf(reservation: Reservation, tickets: list) -> BytesIO:
    pdf_buf = BytesIO()
    width, height = A4
    c = rl_canvas.Canvas(pdf_buf, pagesize=A4)
    show = reservation.event.show
    cx = width / 2

    for name, qr_buf in tickets:
        qr_img = ImageReader(qr_buf)
        qr_size = 220
        qr_x = (width - qr_size) / 2
        qr_y = height / 2 - qr_size / 2 + 20

        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(cx, qr_y + qr_size + 60, show.title)

        c.setFont("Helvetica", 14)
        c.drawCentredString(cx, qr_y + qr_size + 36, f"Ticket für / Ticket for:  {name}")

        c.setLineWidth(0.5)
        c.line(72, qr_y + qr_size + 22, width - 72, qr_y + qr_size + 22)

        c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)

        c.line(72, qr_y - 16, width - 72, qr_y - 16)

        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(cx, qr_y - 36, reservation.event.date_str())

        c.setFont("Helvetica", 12)
        c.drawCentredString(cx, qr_y - 54,
                            f"Einlass {reservation.event.admission_time()}  ·  Beginn {reservation.event.begin_time()}")
        c.drawCentredString(cx, qr_y - 72,
                            "Bitte QR-Code an der Tür vorzeigen  ·  Please show QR code at the door")

        c.showPage()

    c.save()
    pdf_buf.seek(0)
    return pdf_buf


def send_confirmation_mail(reservation: Reservation):
    p = reservation.reservant
    show = reservation.event.show
    guests = list(reservation.guests())
    payment = ReservationPayment.objects.filter(reservation=reservation).first()

    tickets = [(
        f"{p.firstname} {p.surname}",
        _make_qr_buffer({"ticket": str(reservation.id), "event": reservation.event.id}),
    )]
    for guest in guests:
        if guest.ticket_id is None:
            continue
        tickets.append((
            f"{guest.firstname} {guest.surname}",
            _make_qr_buffer({"ticket": str(guest.ticket_id), "event": reservation.event.id}),
        ))

    pdf_buffer = _build_tickets_pdf(reservation, tickets)

    guests_de = ""
    guests_en = ""
    if guests:
        guest_names = "\n".join(f"  - {g.firstname} {g.surname}" for g in guests)
        guests_de = f"\nGäste:\n{guest_names}\n"
        guests_en = f"\nGuests:\n{guest_names}\n"

    payment_de = ""
    payment_en = ""
    if payment:
        ticket_price = payment.ticket_price
        total = payment.total
        payment_de = f"\nPreis pro Ticket: {ticket_price:.2f} EUR\nGesamtbetrag: {total:.2f} EUR\n"
        payment_en = f"\nPrice per ticket: {ticket_price:.2f} EUR\nTotal paid: {total:.2f} EUR\n"

    body = f"""Liebe*r {p.firstname},
vielen Dank für deine Buchung für {show.title} am {reservation.event.date_str()}!

Deine Reservierung:
Name: {p.firstname} {p.surname}
Reservierungs-ID: {reservation.id}
Tickets: {reservation.ticket_count()}{guests_de}{payment_de}
Im Anhang findest du das PDF mit deinen Tickets – für jede Person gibt es einen eigenen QR-Code. Falls ihr nicht gemeinsam ankommt, leite bitte den jeweiligen QR-Code an deine Gäste weiter.

Wir öffnen unsere Tore um {reservation.event.admission_time()}, die Show beginnt um {reservation.event.begin_time()}.

Falls du noch nie in unserem Zelt warst, empfehlen wir dir, dir den Weg über OpenStreetMap zeigen zu lassen:
https://www.openstreetmap.org/directions?from=&to=52.54226,13.43250

Wir freuen uns auf dich im Zirkus Mond – viel Spaß!
<3

—————————————————————————————————————

Dear {p.firstname},
thank you for your booking to {show.title} on the {reservation.event.date_str()}!

Your reservation:
Name: {p.firstname} {p.surname}
Reservation ID: {reservation.id}
Tickets: {reservation.ticket_count()}{guests_en}{payment_en}
The attached PDF contains a individual QR code for each person in your booking. If you're not arriving together, please forward the relevant QR code to your guests.

We open our gates at {reservation.event.admission_time()}, the Show will start at {reservation.event.begin_time()}.

If you have not been to our tent yet, you should ask OpenStreetMap for directions.
https://www.openstreetmap.org/directions?from=&to=52.54226,13.43250

See you at Zirkus Mond and have fun.
<3
"""

    email = EmailMultiAlternatives(
        subject=f'🎪 Thank you for your Reservation for {show.title} 🌙',
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[p.email]
    )
    email.attach(f'tickets_{reservation.id}.pdf', pdf_buffer.read(), 'application/pdf')
    email.send()


# ---------------------------------------------------------------------------
# Purge old payments
# ---------------------------------------------------------------------------

def purge_old_payments(*, confirmed_only: bool = False, dry_run: bool = False):
    cutoff = timezone.now() - datetime.timedelta(days=HALF_YEAR_DAYS)

    qs = ReservationPayment.objects.filter(created__lt=cutoff)
    if confirmed_only:
        qs = qs.filter(status=PaymentStatus.CONFIRMED)

    payments = list(
        qs.select_related(
            "reservation",
            "reservation__reservant",
            "reservation__event",
            "reservation__event__show",
        )
    )

    total_visitors = 0
    for p in payments:
        if p.reservation:
            total_visitors += p.reservation.ticket_count()

    if dry_run:
        return {
            "cutoff": cutoff,
            "payments_found": len(payments),
            "visitors_to_add": total_visitors,
            "deleted_count": 0,
            "final_deleted_visitors": None,
            "dry_run": True,
        }

    with transaction.atomic():
        stats, _ = SiteStats.objects.select_for_update().get_or_create(pk=1)
        SiteStats.objects.filter(pk=stats.pk).update(
            deleted_visitors=F("deleted_visitors") + total_visitors
        )
        deleted_count, _ = qs.delete()
        stats.refresh_from_db()

    return {
        "cutoff": cutoff,
        "payments_found": len(payments),
        "visitors_to_add": total_visitors,
        "deleted_count": deleted_count,
        "final_deleted_visitors": stats.deleted_visitors,
        "dry_run": False,
    }


# ---------------------------------------------------------------------------
# Purge orphaned people and reservations
# ---------------------------------------------------------------------------

def purge_orphan_people_and_reservations(*, dry_run: bool = True):
    reservations_wo_payment_qs = Reservation.objects.filter(
        ~Exists(ReservationPayment.objects.filter(reservation=OuterRef("pk")))
    )
    reservations_to_delete = reservations_wo_payment_qs.count()

    guests_wo_res_qs = Guest.objects.filter(event_reservation__isnull=True)
    guests_to_delete_now = guests_wo_res_qs.count()
    
    # Persons that currently have no Reservation and are not a Guest
    persons_wo_res_now_qs = Person.objects.filter(
        ~Exists(Reservation.objects.filter(reservant=OuterRef("pk"))),
        ~Exists(Guest.objects.filter(pk=OuterRef("pk"))),
    )
    persons_to_delete_now = persons_wo_res_now_qs.count()

    # Approximate "post-phase-1" persons: those who have *no* reservations
    # other than ones we are about to delete, and are not Guests.
    # (For huge datasets, you can skip this extra preview to avoid large IN clauses.)
    res_ids_to_delete = list(reservations_wo_payment_qs.values_list("pk", flat=True))
    persons_wo_res_after_phase1_qs = Person.objects.filter(
         # No surviving reservations (i.e., any reservation NOT in res_ids_to_delete)
        ~Exists(
            Reservation.objects.exclude(pk__in=res_ids_to_delete).filter(
                reservant=OuterRef("pk")
            )
        ),
        ~Exists(Guest.objects.filter(pk=OuterRef("pk"))),
    )
    persons_to_delete_after_phase1 = persons_wo_res_after_phase1_qs.count()

    if dry_run:
        return {
            "dry_run": True,
            "reservations_to_delete": reservations_to_delete,
            "guests_to_delete_now": guests_to_delete_now,
            "persons_to_delete_now": persons_to_delete_now,
            "persons_to_delete_after_phase1": persons_to_delete_after_phase1,
            "deleted_reservations": 0,
            "deleted_guests": 0,
            "deleted_persons": 0,
        }

    with transaction.atomic():
        deleted_reservations, _ = reservations_wo_payment_qs.delete()
        deleted_guests_null, _ = guests_wo_res_qs.delete()

        persons_wo_res_qs = Person.objects.filter(
            ~Exists(Reservation.objects.filter(reservant=OuterRef("pk"))),
            ~Exists(Guest.objects.filter(pk=OuterRef("pk"))),
        )
        deleted_persons, _ = persons_wo_res_qs.delete()

    return {
        "dry_run": False,
        "reservations_to_delete": reservations_to_delete,
        "guests_to_delete_now": guests_to_delete_now,
        "persons_to_delete_now": persons_to_delete_now,
        "persons_to_delete_after_phase1": persons_to_delete_after_phase1,
        "deleted_reservations": deleted_reservations,
        "deleted_guests": deleted_guests_null,
        "deleted_persons": deleted_persons,
    }