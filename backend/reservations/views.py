import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from events.models import Event
from newsletter.services import register_newsletter_email
from reservations.models import Reservation
from reservations.payments.services import create_reservation, parse_custom_price
from reservations.serializers import ReservationDetailSerializer, ReservationSerializer
from shows.models import Show


@api_view(["POST"])
@authentication_classes([])
def reserve_api(request: Request, show_id: int) -> Response:
    show = get_object_or_404(Show, pk=show_id)
    serializer = ReservationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    event = get_object_or_404(Event, pk=serializer.validated_data["event_id"], show=show)
    if not event.reservation_open():
        return Response(
            {"error": "Reservations are not open for this event"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if show.base_ticket_price:
        try:
            parse_custom_price(show, serializer.validated_data.get("custom_price"))
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    reservation = create_reservation(
        event=event,
        first_name=serializer.validated_data["first_name"],
        last_name=serializer.validated_data["last_name"],
        email=serializer.validated_data["email"],
        guests=serializer.validated_data.get("guests", []),
    )

    if serializer.validated_data.get("newsletter"):
        register_newsletter_email(serializer.validated_data["email"])

    return Response(
        {"reservation_id": str(reservation.id)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@authentication_classes([])
def reservation_detail(request: Request, reservation_id: uuid.UUID) -> Response:
    reservation = get_object_or_404(
        Reservation.objects.select_related("event__show").prefetch_related("guests"),
        pk=reservation_id,
    )
    serializer = ReservationDetailSerializer(reservation)
    return Response(serializer.data)