import hashlib

import mailchimp_marketing
from django.conf import settings

from newsletter.models import NewsletterRegistration


def register_email_to_mailchimp(email: str) -> None:
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


def register_newsletter_email(email: str) -> None:
    normalized_email = email.strip().lower()
    NewsletterRegistration.objects.get_or_create(email=normalized_email)
    register_email_to_mailchimp(normalized_email)
