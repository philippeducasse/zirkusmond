from django.test import TestCase

from newsletter.models import NewsletterRegistration
from newsletter.services import register_newsletter_email


class RegisterNewsletterEmailTest(TestCase):
    def test_creates_registration(self):
        register_newsletter_email("test@example.com")
        self.assertEqual(NewsletterRegistration.objects.count(), 1)
        self.assertEqual(NewsletterRegistration.objects.first().email, "test@example.com")

    def test_multiple_calls_create_multiple_records(self):
        register_newsletter_email("a@example.com")
        register_newsletter_email("b@example.com")
        self.assertEqual(NewsletterRegistration.objects.count(), 2)