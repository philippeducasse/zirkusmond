from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reservations", "0006_alter_reservationpayment_custom_ticket_price_payment"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="stripe_payment_intent_id",
            new_name="stripe_session_id",
        ),
        migrations.AddField(
            model_name="payment",
            name="payment_method",
            field=models.CharField(
                choices=[("card", "Card"), ("paypal", "Paypal")],
                max_length=20,
                default="card",
            ),
            preserve_default=False,
        ),
    ]
