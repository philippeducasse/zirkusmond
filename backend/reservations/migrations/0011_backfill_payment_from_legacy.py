from decimal import ROUND_HALF_UP, Decimal

from django.db import migrations

LEGACY_CONFIRMED = "confirmed"
PAYMENT_COMPLETED = "completed"


def backfill(apps, schema_editor):
    """Mirror every confirmed legacy ReservationPayment into a COMPLETED Payment.

    Capacity/revenue/admin queries now read Payment only; without this, bookings
    made through the retired django-payments flow would drop out of every count
    the moment this deploy goes live. Idempotent — skips reservations that
    already have a completed Payment.
    """
    ReservationPayment = apps.get_model("reservations", "ReservationPayment")
    Payment = apps.get_model("reservations", "Payment")
    Guest = apps.get_model("reservations", "Guest")

    legacy = ReservationPayment.objects.filter(
        status=LEGACY_CONFIRMED, reservation__isnull=False
    ).select_related("reservation")

    already_completed = set(
        Payment.objects.filter(status=PAYMENT_COMPLETED, reservation__isnull=False).values_list(
            "reservation_id", flat=True
        )
    )
    guest_counts = {}
    for res_id in legacy.values_list("reservation_id", flat=True):
        guest_counts.setdefault(res_id, 0)
    for res_id in Guest.objects.filter(reservation_id__in=guest_counts).values_list(
        "reservation_id", flat=True
    ):
        guest_counts[res_id] += 1

    to_create = []
    for rp in legacy:
        res_id = rp.reservation_id
        if res_id in already_completed:
            continue
        already_completed.add(res_id)  # guard against duplicate legacy rows

        ticket_count = guest_counts.get(res_id, 0) + 1
        if rp.custom_ticket_price is not None:
            price = int(rp.custom_ticket_price)
        else:
            price = int(
                (Decimal(rp.total) / ticket_count).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )

        to_create.append(
            Payment(
                reservation_id=res_id,
                status=PAYMENT_COMPLETED,
                total=rp.total,
                custom_ticket_price=max(price, 0),
            )
        )

    if to_create:
        Payment.objects.bulk_create(to_create, batch_size=200)
    print(f"  backfill_payment_from_legacy: created {len(to_create)} Payment rows")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("reservations", "0010_alter_payment_payment_method"),
    ]

    operations = [
        migrations.RunPython(backfill, reverse_code=migrations.RunPython.noop),
    ]
