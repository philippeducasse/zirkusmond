import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from newsletter.services import register_newsletter_email

logger = logging.getLogger(__name__)


@api_view(["POST"])
def register(request: Request) -> Response:
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Enter a valid email address"}, status=400)

    register_newsletter_email(email)

    return Response({"success": True}, status=201)
