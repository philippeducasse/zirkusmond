from django.db import migrations


def copy_payments(apps, schema_editor):
    OldPayment = apps.get_model('events', 'ReservationPayment')
    NewPayment = apps.get_model('reservations', 'ReservationPayment')

    for old in OldPayment.objects.select_related('reservation').all():
        if old.reservation_id is None:
            continue
        custom_price = round(old.custom_ticket_price) if old.custom_ticket_price is not None else None
        NewPayment.objects.get_or_create(
            id=old.id,
            defaults=dict(
                reservation_id=old.reservation_id,
                variant=old.variant,
                status=old.status,
                transaction_id=old.transaction_id,
                currency=old.currency,
                total=old.total,
                token=old.token,
                captured_amount=old.captured_amount,
                extra_data=old.extra_data,
                custom_ticket_price=custom_price,
            ),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_reservationpayment'),
    ]

    operations = [
        migrations.RunPython(copy_payments, reverse_code=migrations.RunPython.noop),
    ]
