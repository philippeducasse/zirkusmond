from rest_framework.serializers import ModelSerializer

from events.serializers import BasicEventSerializer, EventSerializer
from shows.models import Show


class ShowCardSerializer(ModelSerializer):
    upcoming_events = BasicEventSerializer(read_only=True, many=True, source="future_events")

    class Meta:
        model = Show
        fields = ["id", "title", "card_image", "upcoming_events"]


class ShowDetailSerializer(ModelSerializer):
    upcoming_events = EventSerializer(read_only=True, many=True, source="future_events")

    class Meta:
        model = Show
        fields = [
            "id",
            "title",
            "description",
            "cast",
            "card_image",
            "banner_image",
            "video_link",
            "website_link",
            "base_ticket_price",
            "min_ticket_price",
            "max_ticket_price",
            "reservation_price",
            "third_party_reservation",
            "third_party_reservation_link",
            "upcoming_events",
            "last_modified",
        ]
