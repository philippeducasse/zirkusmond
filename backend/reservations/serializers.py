from rest_framework import serializers


class GuestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False, allow_blank=True)


class ReservationSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    email = serializers.EmailField()
    attendee_count = serializers.IntegerField(min_value=1, max_value=10)
    payment_method = serializers.CharField()
    custom_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    newsletter = serializers.BooleanField(required=False, default=False)
    guests = GuestSerializer(many=True, required=False)

    def validate_attendee_count(self, value):
        if value > 10:
            raise serializers.ValidationError("Maximum 10 attendees allowed.")
        return value
