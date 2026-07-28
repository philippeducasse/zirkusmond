from newsletter.models import NewsletterRegistration


def register_newsletter_email(email: str) -> None:
    NewsletterRegistration.objects.get_or_create(email=email.strip().lower())
