import hashlib
import logging

import mailchimp_marketing
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from mailchimp_marketing.api_client import ApiClientError
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from newsletter.models import NewsletterRegistration

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
    NewsletterRegistration.objects.get_or_create(email=email)

    # Add to Mailchimp
    try:
        client = mailchimp_marketing.Client()
        client.set_config(
            {"api_key": settings.NEWSLETTER_TOKEN, "server": settings.MAILCHIMP_SERVER_PREFIX}
        )

        subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

        client.lists.set_list_member(
            settings.MAILCHIMP_AUDIENCE_ID,
            subscriber_hash,
            {"email_address": email, "status_if_new": "subscribed"},
        )
        logger.info(f"Email {email} successfully added to mailchimp")

    except ApiClientError as error:
        logger.error(f"Mailchimp API error: {error.text}")
        # Don't fail the request if Mailchimp fails
    except Exception as error:
        logger.error(f"Unexpected error adding to Mailchimp: {error}")
        # Don't fail the request if Mailchimp fails

    return Response({"success": True}, status=201)
