from typing import Any

from django.conf import settings
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
    custom_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    newsletter = serializers.BooleanField(required=False, default=False)
    guests = GuestSerializer(many=True, required=False)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        guests = data.get("guests", [])
        if len(guests) != data["attendee_count"] - 1:
            raise serializers.ValidationError(
                {"guests": "guests count must equal attendee_count - 1"}
            )
        return data
