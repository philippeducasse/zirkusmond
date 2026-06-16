from newsletter.models import NewsletterRegistration


def register_newsletter_email(email: str) -> None:
    NewsletterRegistration.objects.create(email=email)
