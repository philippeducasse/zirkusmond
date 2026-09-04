import hashlib
import logging

import mailchimp_marketing
from django.conf import settings
from mailchimp_marketing.api_client import ApiClientError

from newsletter.models import NewsletterRegistration

logger = logging.getLogger(__name__)


def register_email_to_mailchimp(email: str) -> None:
    client = mailchimp_marketing.Client()
    client.set_config(
        {"api_key": settings.NEWSLETTER_TOKEN, "server": settings.MAILCHIMP_SERVER_PREFIX}
    )

    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

    try:
        client.lists.set_list_member(
            settings.MAILCHIMP_AUDIENCE_ID,
            subscriber_hash,
            {"email_address": email, "status_if_new": "subscribed"},
        )
    except ApiClientError as e:
        logger.error(f"Mailchimp API error for {email}: {e.text}")
        raise


def register_newsletter_email(email: str) -> None:
    normalized_email = email.strip().lower()
    NewsletterRegistration.objects.get_or_create(email=normalized_email)
    register_email_to_mailchimp(normalized_email)
