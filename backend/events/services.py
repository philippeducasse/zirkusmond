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

from reservations.models import Reservation
from reservations.payments.models import ReservationPayment
from stats.models import SiteStats
from payments import PaymentStatus

logger = logging.getLogger(__name__)

HALF_YEAR_DAYS = 220  # ≈6 months


def _make_qr_buffer(data: dict) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def _build_tickets_pdf(reservation: Reservation, tickets: list) -> BytesIO:
    pdf_buffer = BytesIO()
    width, height = A4
    canvas = rl_canvas.Canvas(pdf_buffer, pagesize=A4)
    show = reservation.event.show
    center_x = width / 2

    for name, qr_buffer in tickets:
        qr_image = ImageReader(qr_buffer)
        qr_size = 220
        qr_x = (width - qr_size) / 2
        qr_y = height / 2 - qr_size / 2 + 20

        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawCentredString(center_x, qr_y + qr_size + 60, show.title)

        canvas.setFont("Helvetica", 14)
        canvas.drawCentredString(center_x, qr_y + qr_size + 36, f"Ticket für / Ticket for:  {name}")

        canvas.setLineWidth(0.5)
        canvas.line(72, qr_y + qr_size + 22, width - 72, qr_y + qr_size + 22)

        canvas.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)

        canvas.line(72, qr_y - 16, width - 72, qr_y - 16)

        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(center_x, qr_y - 36, reservation.event.date_str())

        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(center_x, qr_y - 54,
                            f"Einlass {reservation.event.admission_time()}  ·  Beginn {reservation.event.begin_time()}")
        canvas.drawCentredString(center_x, qr_y - 72,
                            "Bitte QR-Code an der Tür vorzeigen  ·  Please show QR code at the door")

        canvas.showPage()

    canvas.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def send_confirmation_mail(reservation: Reservation):
    logger.info(
        'send_confirmation_mail: reservation=%s event=%s email=%s tickets=%s',
        reservation.id, reservation.event, reservation.email, reservation.ticket_count(),
    )
    show = reservation.event.show
    guests = list(reservation.guests.all())
    payment = ReservationPayment.objects.filter(reservation=reservation).first()

    tickets = [(
        f"{reservation.first_name} {reservation.last_name}",
        _make_qr_buffer({"ticket": str(reservation.id), "event": reservation.event.id}),
    )]
    for guest in guests:
        if guest.ticket_id is None:
            continue
        tickets.append((
            f"{guest.first_name} {guest.last_name}",
            _make_qr_buffer({"ticket": str(guest.ticket_id), "event": reservation.event.id}),
        ))

    pdf_buffer = _build_tickets_pdf(reservation, tickets)

    guests_de = ""
    guests_en = ""
    if guests:
        guest_names = "\n".join(f"  - {guest.first_name} {guest.last_name}" for guest in guests)
        guests_de = f"\nGäste:\n{guest_names}\n"
        guests_en = f"\nGuests:\n{guest_names}\n"

    payment_de = ""
    payment_en = ""
    if payment:
        ticket_price = payment.ticket_price
        total = payment.total
        payment_de = f"\nPreis pro Ticket: {ticket_price:.2f} EUR\nGesamtbetrag: {total:.2f} EUR\n"
        payment_en = f"\nPrice per ticket: {ticket_price:.2f} EUR\nTotal paid: {total:.2f} EUR\n"

    body = f"""Liebe*r {reservation.first_name},
vielen Dank für deine Buchung für {show.title} am {reservation.event.date_str()}!

Deine Reservierung:
Name: {reservation.first_name} {reservation.last_name}
Reservierungs-ID: {reservation.id}
Tickets: {reservation.ticket_count()}{guests_de}{payment_de}
Im Anhang findest du das PDF mit deinen Tickets – für jede Person gibt es einen eigenen QR-Code. Falls ihr nicht gemeinsam ankommt, leite bitte den jeweiligen QR-Code an deine Gäste weiter.

Wir öffnen unsere Tore um {reservation.event.admission_time()}, die Show beginnt um {reservation.event.begin_time()}.

Falls du noch nie in unserem Zelt warst, empfehlen wir dir, dir den Weg über OpenStreetMap zeigen zu lassen:
https://www.openstreetmap.org/directions?from=&to=52.54226,13.43250

Wir freuen uns auf dich im Zirkus Mond – viel Spaß!
<3

—————————————————————————————————————

Dear {reservation.first_name},
thank you for your booking to {show.title} on the {reservation.event.date_str()}!

Your reservation:
Name: {reservation.first_name} {reservation.last_name}
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
        to=[reservation.email]
    )
    email.attach(f'tickets_{reservation.id}.pdf', pdf_buffer.read(), 'application/pdf')
    email.send()
    logger.info('confirmation email delivered for reservation=%s', reservation.id)


def purge_old_payments(*, confirmed_only: bool = False, dry_run: bool = False):
    cutoff = timezone.now() - datetime.timedelta(days=HALF_YEAR_DAYS)

    payments_qs = ReservationPayment.objects.filter(created__lt=cutoff)
    if confirmed_only:
        payments_qs = payments_qs.filter(status=PaymentStatus.CONFIRMED)

    payments = list(
        payments_qs.select_related(
            "reservation",
            "reservation__event",
            "reservation__event__show",
        )
    )

    total_visitors = 0
    for payment in payments:
        if payment.reservation:
            total_visitors += payment.reservation.ticket_count()

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
        deleted_count, _ = payments_qs.delete()
        stats.refresh_from_db()

    return {
        "cutoff": cutoff,
        "payments_found": len(payments),
        "visitors_to_add": total_visitors,
        "deleted_count": deleted_count,
        "final_deleted_visitors": stats.deleted_visitors,
        "dry_run": False,
    }


def purge_orphan_reservations(*, dry_run: bool = True):
    orphan_reservations_qs = Reservation.objects.filter(
        ~Exists(ReservationPayment.objects.filter(reservation=OuterRef("pk")))
    )
    reservations_to_delete = orphan_reservations_qs.count()

    if dry_run:
        return {
            "dry_run": True,
            "reservations_to_delete": reservations_to_delete,
            "deleted_reservations": 0,
        }

    with transaction.atomic():
        deleted_reservations, _ = orphan_reservations_qs.delete()

    return {
        "dry_run": False,
        "reservations_to_delete": reservations_to_delete,
        "deleted_reservations": deleted_reservations,
    }