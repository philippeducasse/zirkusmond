from rest_framework.serializers import ModelSerializer

from events.models import Event


class BasicEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ["time_and_date"]


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "elaborate_date_str",
            "admission_time",
            "begin_time",
            "reservation_capacity",
            "reservation_open",
        ]
