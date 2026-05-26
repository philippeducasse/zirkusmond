from django.db import migrations


def rename_variant(apps, schema_editor):
    ReservationPayment = apps.get_model('reservations', 'ReservationPayment')
    ReservationPayment.objects.filter(variant='bank card').update(variant='stripe')


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_migrate_payment_data'),
    ]

    operations = [
        migrations.RunPython(rename_variant, migrations.RunPython.noop),
    ]