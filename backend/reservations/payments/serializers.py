from rest_framework import serializers

from reservations.payments.models import Payment


class CreatePaymentIntentSerializer(serializers.Serializer):
    custom_ticket_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class PaymentIntentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "client_secret"]

    client_secret = serializers.SerializerMethodField()

    def get_client_secret(self, obj: Payment) -> str | None:
        # This will be set on the object after Stripe intent creation
        return getattr(obj, "_client_secret", None)
