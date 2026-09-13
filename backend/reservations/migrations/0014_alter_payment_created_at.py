from django.db import migrations

LEGACY_CONFIRMED = "confirmed"
PAYMENT_COMPLETED = "completed"


def update_created_at_field_on_payments(apps, schema_editor):
    """Migration 0011 successfully migrated old ReservationPayment objects to the new Payment objects.
    However, the created_at date was not copied, resulting in thousands of new payment objects with the
    same creation date. This migration fixes that.
    """
    ReservationPayment = apps.get_model("reservations", "ReservationPayment")
    Payment = apps.get_model("reservations", "Payment")

    original_dates_by_reservation = dict(
        ReservationPayment.objects.filter(
            status=LEGACY_CONFIRMED, reservation__isnull=False, created__isnull=False
        ).values_list("reservation_id", "created")
    )
    payments_to_update = list(
        Payment.objects.filter(
            status=PAYMENT_COMPLETED, reservation_id__in=original_dates_by_reservation.keys()
        )
    )

    for payment in payments_to_update:
        payment.created_at = original_dates_by_reservation[payment.reservation_id]

    Payment.objects.bulk_update(payments_to_update, ["created_at"], batch_size=500)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("reservations", "0013_alter_payment_status"),
    ]

    operations = [
        migrations.RunPython(
            update_created_at_field_on_payments, reverse_code=migrations.RunPython.noop
        ),
    ]
