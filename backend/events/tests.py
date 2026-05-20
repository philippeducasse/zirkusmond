from django.test import TestCase, override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from io import BytesIO
from PIL import Image
import smtplib
import uuid
from .models import Show, Event, Person, Reservation, Guest, ReservationPayment
from .forms import ReservationForm


def create_test_image():
    """Helper function to create a simple test image in memory."""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class EmailBackendVerificationTest(TestCase):
    """
    Verify email backend configuration and SMTP connectivity.
    """

    def test_email_backend_configuration(self):
        """Verify that the correct email backend is configured."""
        print("\n" + "="*60)
        print("EMAIL BACKEND VERIFICATION")
        print("="*60)
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print("="*60)

        # Verify we're using SMTP backend, not console or locmem
        self.assertEqual(
            settings.EMAIL_BACKEND,
            'django.core.mail.backends.smtp.EmailBackend',
            "Email backend should be SMTP for real email sending"
        )

    def test_smtp_connection(self):
        """Test direct SMTP connection to verify server is reachable."""
        print("\n" + "="*60)
        print("SMTP CONNECTION TEST")
        print("="*60)

        try:
            # Try to connect to SMTP server
            if settings.EMAIL_USE_TLS:
                print(f"Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} with TLS...")
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                print(f"Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)

            # Try to login
            print(f"Logging in as {settings.EMAIL_HOST_USER}...")
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("✓ SMTP connection successful!")
            print("✓ Authentication successful!")

            server.quit()
            print("="*60)
        except Exception as e:
            print(f"✗ SMTP connection failed: {str(e)}")
            print("="*60)
            self.fail(f"SMTP connection test failed: {str(e)}")

    def test_send_simple_email_directly(self):
        """Send a simple test email using Django's send_mail."""
        print("\n" + "="*60)
        print("DIRECT EMAIL SEND TEST")
        print("="*60)

        test_email = "ducassephi@hotmail.fr"

        try:
            num_sent = send_mail(
                subject='Test Email from Django Test Suite',
                message='This is a test email to verify SMTP is working correctly.\n\nIf you receive this, the email system is working!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False
            )

            print(f"✓ send_mail() returned: {num_sent}")
            print(f"✓ Email sent to {test_email}")
            print("="*60)

            self.assertEqual(num_sent, 1, "send_mail should return 1 for successful send")
        except Exception as e:
            print(f"✗ Email send failed: {str(e)}")
            print(f"✗ Exception type: {type(e).__name__}")
            print("="*60)
            self.fail(f"Direct email send failed: {str(e)}")


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class SendConfirmationMailTestCase(TestCase):
    """
    Test case for send_confirmation_mail() with real email sending.
    This test creates real database objects and sends actual emails.
    No mocking is used.
    """

    def setUp(self):
        """
        Create a Show and Event that will be used for all test reservations.
        """
        # Create a show
        self.show = Show.objects.create(
            title="Test Circus Show - Email Test",
            description="This is a test show for email confirmation testing.",
            cast="Test performers",
            video_link="",
            website_link="",
            card_image=create_test_image(),
            private=False,
            reservation_price=10.00,
            ticket_price=15.00,
        )

        # Create an event scheduled for next week
        next_week = timezone.now() + timedelta(days=7)
        admission_time = next_week.replace(hour=19, minute=0, second=0, microsecond=0)
        begin_time = next_week.replace(hour=20, minute=0, second=0, microsecond=0)

        self.event = Event.objects.create(
            show=self.show,
            admission=admission_time,
            begin=begin_time,
            reservation_capacity=150,
            open_for_reservation=True
        )

    def test_send_confirmation_emails_to_all_addresses(self):
        """
        Test sending confirmation emails to all three email addresses.
        This will actually send real emails to:
        - ducassephi@hotmail.fr
        - philocircus@gmail.com
        - info@philippeducasse.com
        """
        # Define the email addresses to test
        email_addresses = [
            {
                'email': 'ducassephi@hotmail.fr',
                'firstname': 'Philippe',
                'surname': 'Ducasse',
            },
            {
                'email': 'philocircus@gmail.com',
                'firstname': 'Philo',
                'surname': 'Circus',
            },
            {
                'email': 'info@philippeducasse.com',
                'firstname': 'Info',
                'surname': 'Contact',
            },
        ]

        # Create reservations and send emails for each address
        for recipient in email_addresses:
            with self.subTest(email=recipient['email']):
                # Create a person
                person = Person.objects.create(
                    firstname=recipient['firstname'],
                    surname=recipient['surname'],
                    email=recipient['email'],
                    street='Test Street 123',
                    zipcode=12345,
                    town='Test City',
                    phonenumber='+49123456789'
                )

                # Create a reservation
                reservation = Reservation.objects.create(
                    event=self.event,
                    reservant=person
                )

                # Send the confirmation email (this will actually send the email)
                # The method will raise an exception if it fails
                try:
                    reservation.send_confirmation_mail()
                    print(f"✓ Successfully sent confirmation email to {recipient['email']}")
                except Exception as e:
                    self.fail(f"Failed to send email to {recipient['email']}: {str(e)}")

        print("\n" + "="*60)
        print("EMAIL TEST SUMMARY")
        print("="*60)
        print(f"Show: {self.show.title}")
        print(f"Event: {self.event.time_and_date()}")
        print(f"Emails sent to: {len(email_addresses)} addresses")
        for recipient in email_addresses:
            print(f"  - {recipient['email']}")
        print("="*60)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class SendConfirmationMailIndividualTests(TestCase):
    """
    Individual test methods for each email address.
    Run these separately if you want to test one email at a time.
    """

    def setUp(self):
        """Create Show and Event for testing."""
        self.show = Show.objects.create(
            title="Individual Test Show",
            description="Testing individual email sends",
            cast="Test cast",
            card_image=create_test_image(),
            private=False,
            reservation_price=10.00,
            ticket_price=15.00,
        )

        next_week = timezone.now() + timedelta(days=7)
        admission_time = next_week.replace(hour=19, minute=0, second=0, microsecond=0)
        begin_time = next_week.replace(hour=20, minute=0, second=0, microsecond=0)

        self.event = Event.objects.create(
            show=self.show,
            admission=admission_time,
            begin=begin_time,
            reservation_capacity=150,
            open_for_reservation=True
        )

    def test_send_to_ducassephi_hotmail(self):
        """Send confirmation email to ducassephi@hotmail.fr"""
        person = Person.objects.create(
            firstname='Philippe',
            surname='Ducasse',
            email='ducassephi@hotmail.fr',
            street='Test Street 123',
            zipcode=12345,
            town='Test City',
            phonenumber='+49123456789'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # This will actually send the email
        reservation.send_confirmation_mail()
        print("✓ Email sent to ducassephi@hotmail.fr")

    def test_send_to_philocircus_gmail(self):
        """Send confirmation email to philocircus@gmail.com"""
        person = Person.objects.create(
            firstname='Philo',
            surname='Circus',
            email='philocircus@gmail.com',
            street='Circus Street 456',
            zipcode=54321,
            town='Circus Town',
            phonenumber='+49987654321'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # This will actually send the email
        reservation.send_confirmation_mail()
        print(f"✓ Email sent to philocircus@gmail.com")

    def test_send_to_info_philippeducasse(self):
        """Send confirmation email to info@philippeducasse.com"""
        person = Person.objects.create(
            firstname='Info',
            surname='Contact',
            email='info@philippeducasse.com',
            street='Contact Street 789',
            zipcode=98765,
            town='Contact City',
            phonenumber='+49555123456'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # This will actually send the email
        reservation.send_confirmation_mail()
        print(f"✓ Email sent to info@philippeducasse.com")


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class SendConfirmationMailWithGuestsTest(TestCase):
    """
    Test case for send_confirmation_mail() with reservations that include guests.
    These tests verify that confirmation emails are sent correctly when a
    reservation includes additional guests beyond the primary reservant.
    """

    def setUp(self):
        """Create Show and Event for testing."""
        self.show = Show.objects.create(
            title="Guest Test Show",
            description="Testing reservations with guests",
            cast="Test cast",
            card_image=create_test_image(),
            private=False,
            reservation_price=10.00,
            ticket_price=15.00,
        )

        next_week = timezone.now() + timedelta(days=7)
        admission_time = next_week.replace(hour=19, minute=0, second=0, microsecond=0)
        begin_time = next_week.replace(hour=20, minute=0, second=0, microsecond=0)

        self.event = Event.objects.create(
            show=self.show,
            admission=admission_time,
            begin=begin_time,
            reservation_capacity=150,
            open_for_reservation=True
        )

    def test_send_to_hotmail_with_one_guest(self):
        """Send confirmation email with 1 guest to ducassephi@hotmail.fr"""
        # Create the main reservant
        person = Person.objects.create(
            firstname='Philippe',
            surname='Ducasse',
            email='ducassephi@hotmail.fr',
            street='Test Street 123',
            zipcode=12345,
            town='Test City',
            phonenumber='+49123456789'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # Add one guest
        Guest.objects.create(
            firstname='Guest',
            surname='One',
            email='guest1@example.com',
            event_reservation=reservation
        )

        # Verify ticket count includes guest
        self.assertEqual(reservation.ticket_count(), 2, "Should have 2 tickets (reservant + 1 guest)")

        # Send the confirmation email
        reservation.send_confirmation_mail()
        print("✓ Email sent to ducassephi@hotmail.fr with 1 guest (total: 2 tickets)")

    def test_send_to_gmail_with_multiple_guests(self):
        """Send confirmation email with multiple guests to philocircus@gmail.com"""
        # Create the main reservant
        person = Person.objects.create(
            firstname='Philo',
            surname='Circus',
            email='philocircus@gmail.com',
            street='Circus Street 456',
            zipcode=54321,
            town='Circus Town',
            phonenumber='+49987654321'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # Add multiple guests
        Guest.objects.create(
            firstname='Alice',
            surname='Wonderland',
            email='alice@example.com',
            event_reservation=reservation
        )

        Guest.objects.create(
            firstname='Bob',
            surname='Builder',
            email='bob@example.com',
            event_reservation=reservation
        )

        Guest.objects.create(
            firstname='Charlie',
            surname='Chaplin',
            email='charlie@example.com',
            event_reservation=reservation
        )

        # Verify ticket count includes all guests
        self.assertEqual(reservation.ticket_count(), 4, "Should have 4 tickets (reservant + 3 guests)")

        # Send the confirmation email
        reservation.send_confirmation_mail()
        print(f"✓ Email sent to philocircus@gmail.com with 3 guests (total: 4 tickets)")

    def test_send_to_info_with_family_guests(self):
        """Send confirmation email with family members as guests to info@philippeducasse.com"""
        # Create the main reservant
        person = Person.objects.create(
            firstname='Info',
            surname='Contact',
            email='info@philippeducasse.com',
            street='Contact Street 789',
            zipcode=98765,
            town='Contact City',
            phonenumber='+49555123456'
        )

        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person
        )

        # Add family members as guests
        Guest.objects.create(
            firstname='Maria',
            surname='Contact',
            email='maria@example.com',
            street='Contact Street 789',
            zipcode=98765,
            town='Contact City',
            event_reservation=reservation
        )

        Guest.objects.create(
            firstname='Sophie',
            surname='Contact',
            email='sophie@example.com',
            street='Contact Street 789',
            zipcode=98765,
            town='Contact City',
            event_reservation=reservation
        )

        # Verify ticket count
        self.assertEqual(reservation.ticket_count(), 3, "Should have 3 tickets (reservant + 2 family members)")

        # Send the confirmation email
        reservation.send_confirmation_mail()
        print(f"✓ Email sent to info@philippeducasse.com with 2 family guests (total: 3 tickets)")

    def test_send_to_all_addresses_with_varying_guest_counts(self):
        """
        Test sending confirmation emails to all three addresses with different numbers of guests.
        This comprehensive test creates multiple reservations with varying guest counts.
        """
        test_scenarios = [
            {
                'reservant': {
                    'firstname': 'Philippe',
                    'surname': 'Ducasse',
                    'email': 'ducassephi@hotmail.fr',
                    'street': 'Test Street 123',
                    'zipcode': 12345,
                    'town': 'Test City',
                    'phonenumber': '+49123456789'
                },
                'guests': [
                    {'firstname': 'Guest', 'surname': 'One'},
                ],
                'expected_count': 2
            },
            {
                'reservant': {
                    'firstname': 'Philo',
                    'surname': 'Circus',
                    'email': 'philocircus@gmail.com',
                    'street': 'Circus Street 456',
                    'zipcode': 54321,
                    'town': 'Circus Town',
                    'phonenumber': '+49987654321'
                },
                'guests': [
                    {'firstname': 'Alice', 'surname': 'Wonderland'},
                    {'firstname': 'Bob', 'surname': 'Builder'},
                    {'firstname': 'Charlie', 'surname': 'Chaplin'},
                    {'firstname': 'Diana', 'surname': 'Prince'},
                ],
                'expected_count': 5
            },
            {
                'reservant': {
                    'firstname': 'Info',
                    'surname': 'Contact',
                    'email': 'info@philippeducasse.com',
                    'street': 'Contact Street 789',
                    'zipcode': 98765,
                    'town': 'Contact City',
                    'phonenumber': '+49555123456'
                },
                'guests': [
                    {'firstname': 'Maria', 'surname': 'Contact'},
                    {'firstname': 'Sophie', 'surname': 'Contact'},
                    {'firstname': 'Lucas', 'surname': 'Contact'},
                ],
                'expected_count': 4
            },
        ]

        for scenario in test_scenarios:
            with self.subTest(email=scenario['reservant']['email']):
                # Create the reservant
                person = Person.objects.create(**scenario['reservant'])

                # Create the reservation
                reservation = Reservation.objects.create(
                    event=self.event,
                    reservant=person
                )

                # Add guests
                for guest_data in scenario['guests']:
                    Guest.objects.create(
                        firstname=guest_data['firstname'],
                        surname=guest_data['surname'],
                        email=f"{guest_data['firstname'].lower()}@example.com",
                        event_reservation=reservation
                    )

                # Verify ticket count
                self.assertEqual(
                    reservation.ticket_count(),
                    scenario['expected_count'],
                    f"Should have {scenario['expected_count']} tickets"
                )

                # Send the confirmation email
                try:
                    reservation.send_confirmation_mail()
                    print(f"✓ Email sent to {scenario['reservant']['email']} "
                          f"with {len(scenario['guests'])} guest(s) "
                          f"(total: {scenario['expected_count']} tickets)")
                except Exception as e:
                    self.fail(f"Failed to send email to {scenario['reservant']['email']}: {str(e)}")

        print("\n" + "="*60)
        print("GUEST EMAIL TEST SUMMARY")
        print("="*60)
        print(f"Show: {self.show.title}")
        print(f"Event: {self.event.time_and_date()}")
        print(f"Total test scenarios: {len(test_scenarios)}")
        for scenario in test_scenarios:
            print(f"  - {scenario['reservant']['email']}: "
                  f"{len(scenario['guests'])} guest(s), "
                  f"{scenario['expected_count']} total tickets")
        print("="*60)


class ReservationFormTest(TestCase):

    def setUp(self):
        self.show = Show.objects.create(
            title='Form Test Show',
            description='desc',
            cast='cast',
            card_image=create_test_image(),
            private=False,
        )
        self.future = timezone.now() + timedelta(days=7)
        self.past = timezone.now() - timedelta(days=1)

    def _make_event(self, begin, open_for_reservation=True, capacity=150):
        return Event.objects.create(
            show=self.show,
            admission=begin - timedelta(hours=1),
            begin=begin,
            reservation_capacity=capacity,
            open_for_reservation=open_for_reservation,
        )

    def test_future_open_event_included(self):
        event = self._make_event(self.future)
        form = ReservationForm(self.show)
        self.assertIn(event, form.fields['event'].queryset)

    def test_past_event_excluded(self):
        event = self._make_event(self.past)
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields['event'].queryset)

    def test_manually_closed_event_excluded(self):
        event = self._make_event(self.future, open_for_reservation=False)
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields['event'].queryset)

    def test_over_capacity_event_excluded(self):
        event = self._make_event(self.future, capacity=1)
        person = Person.objects.create(firstname='A', surname='B', email='a@b.com')
        reservation = Reservation.objects.create(event=event, reservant=person)
        # add a second person to exceed capacity of 1
        person2 = Person.objects.create(firstname='C', surname='D', email='c@d.com')
        reservation2 = Reservation.objects.create(event=event, reservant=person2)
        ReservationPayment.from_reservation(reservation, variant='paypal').save()
        ReservationPayment.from_reservation(reservation2, variant='paypal').save()
        form = ReservationForm(self.show)
        self.assertNotIn(event, form.fields['event'].queryset)

    def test_only_open_events_from_this_show_included(self):
        open_event = self._make_event(self.future)
        past_event = self._make_event(self.past)
        closed_event = self._make_event(self.future, open_for_reservation=False)
        form = ReservationForm(self.show)
        qs = form.fields['event'].queryset
        self.assertIn(open_event, qs)
        self.assertNotIn(past_event, qs)
        self.assertNotIn(closed_event, qs)


class ShowPriceValidationTest(TestCase):
    """Tests for Show model price validation."""

    def setUp(self):
        """Create a base show for testing."""
        self.show_data = {
            'title': 'Test Show',
            'description': 'Test description',
            'cast': 'Test cast',
            'card_image': create_test_image(),
            'private': False,
        }

    def test_valid_prices(self):
        """Test that valid price configurations pass validation."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            min_ticket_price=Decimal('10.00'),
            max_ticket_price=Decimal('30.00'),
            reservation_price=Decimal('5.00'),
        )
        # Should not raise
        show.full_clean()

    def test_negative_ticket_price_raises_error(self):
        """Test that negative ticket_price raises ValidationError."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('-10.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('ticket_price', ctx.exception.message_dict)

    def test_negative_min_ticket_price_raises_error(self):
        """Test that negative min_ticket_price raises ValidationError."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            min_ticket_price=Decimal('-5.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('min_ticket_price', ctx.exception.message_dict)

    def test_negative_max_ticket_price_raises_error(self):
        """Test that negative max_ticket_price raises ValidationError."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            max_ticket_price=Decimal('-5.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('max_ticket_price', ctx.exception.message_dict)

    def test_negative_reservation_price_raises_error(self):
        """Test that negative reservation_price raises ValidationError."""
        show = Show(
            **self.show_data,
            reservation_price=Decimal('-5.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('reservation_price', ctx.exception.message_dict)

    def test_min_price_greater_than_ticket_price_raises_error(self):
        """Test that min_ticket_price > ticket_price raises ValidationError."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('15.00'),
            min_ticket_price=Decimal('20.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('min_ticket_price', ctx.exception.message_dict)

    def test_max_price_less_than_ticket_price_raises_error(self):
        """Test that max_ticket_price < ticket_price raises ValidationError."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            max_ticket_price=Decimal('15.00'),
        )
        with self.assertRaises(ValidationError) as ctx:
            show.full_clean()
        self.assertIn('max_ticket_price', ctx.exception.message_dict)

    def test_min_equals_ticket_price_is_valid(self):
        """Test that min_ticket_price == ticket_price is valid."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            min_ticket_price=Decimal('20.00'),
        )
        # Should not raise
        show.full_clean()

    def test_max_equals_ticket_price_is_valid(self):
        """Test that max_ticket_price == ticket_price is valid."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            max_ticket_price=Decimal('20.00'),
        )
        # Should not raise
        show.full_clean()

    def test_prices_without_ticket_price_is_valid(self):
        """Test that min/max prices without ticket_price don't raise errors."""
        show = Show(
            **self.show_data,
            min_ticket_price=Decimal('10.00'),
            max_ticket_price=Decimal('30.00'),
        )
        # Should not raise - no ticket_price to compare against
        show.full_clean()

    def test_effective_min_price_uses_custom_value(self):
        """Test get_effective_min_price returns custom min when set."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            min_ticket_price=Decimal('12.00'),
        )
        self.assertEqual(show.get_effective_min_price(Decimal('20.00')), Decimal('12.00'))

    def test_effective_min_price_defaults_to_base_minus_10(self):
        """Test get_effective_min_price defaults to base_price - 10."""
        show = Show(**self.show_data, ticket_price=Decimal('20.00'))
        self.assertEqual(show.get_effective_min_price(Decimal('20.00')), Decimal('10.00'))

    def test_effective_min_price_floors_at_5(self):
        """Test get_effective_min_price doesn't go below 5 EUR."""
        show = Show(**self.show_data, ticket_price=Decimal('8.00'))
        self.assertEqual(show.get_effective_min_price(Decimal('8.00')), Decimal('5.00'))

    def test_effective_max_price_uses_custom_value(self):
        """Test get_effective_max_price returns custom max when set."""
        show = Show(
            **self.show_data,
            ticket_price=Decimal('20.00'),
            max_ticket_price=Decimal('35.00'),
        )
        self.assertEqual(show.get_effective_max_price(Decimal('20.00')), Decimal('35.00'))

    def test_effective_max_price_defaults_to_base_plus_10(self):
        """Test get_effective_max_price defaults to base_price + 10."""
        show = Show(**self.show_data, ticket_price=Decimal('20.00'))
        self.assertEqual(show.get_effective_max_price(Decimal('20.00')), Decimal('30.00'))


class ReservationPaymentValidationTest(TestCase):
    """Tests for ReservationPayment price validation."""

    def setUp(self):
        """Create show, event, person, and reservation for testing."""
        self.show = Show.objects.create(
            title='Payment Test Show',
            description='Test description',
            cast='Test cast',
            card_image=create_test_image(),
            private=False,
            ticket_price=Decimal('20.00'),
            min_ticket_price=Decimal('10.00'),
            max_ticket_price=Decimal('30.00'),
        )

        next_week = timezone.now() + timedelta(days=7)
        self.event = Event.objects.create(
            show=self.show,
            admission=next_week.replace(hour=19, minute=0),
            begin=next_week.replace(hour=20, minute=0),
            reservation_capacity=150,
        )

        self.person = Person.objects.create(
            firstname='Test',
            surname='User',
            email='test@example.com',
        )

        self.reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )

    def test_ticket_price_returns_custom_price_when_set(self):
        """Test that ticket_price property returns custom_ticket_price when set."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('25.00')
        self.assertEqual(payment.ticket_price, Decimal('25.00'))

    def test_ticket_price_returns_show_price_when_no_custom(self):
        """Test that ticket_price property returns show's ticket_price when no custom."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.ticket_price, Decimal('20.00'))

    def test_ticket_price_defaults_to_15_when_no_show_price(self):
        """Test that ticket_price defaults to 15 when show has no ticket_price."""
        self.show.ticket_price = None
        self.show.save()
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        self.assertEqual(payment.ticket_price, Decimal('15.0'))

    def test_validate_custom_price_within_range_returns_true(self):
        """Test that custom price within range passes validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('15.00')
        self.assertTrue(payment.validate_custom_price(Decimal('20.00')))

    def test_validate_custom_price_at_min_returns_true(self):
        """Test that custom price at minimum passes validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('10.00')
        self.assertTrue(payment.validate_custom_price(Decimal('20.00')))

    def test_validate_custom_price_at_max_returns_true(self):
        """Test that custom price at maximum passes validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('30.00')
        self.assertTrue(payment.validate_custom_price(Decimal('20.00')))

    def test_validate_custom_price_below_min_returns_false(self):
        """Test that custom price below minimum fails validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('5.00')
        self.assertFalse(payment.validate_custom_price(Decimal('20.00')))

    def test_validate_custom_price_above_max_returns_false(self):
        """Test that custom price above maximum fails validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('35.00')
        self.assertFalse(payment.validate_custom_price(Decimal('20.00')))

    def test_validate_custom_price_none_returns_true(self):
        """Test that None custom price passes validation."""
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = None
        self.assertTrue(payment.validate_custom_price(Decimal('20.00')))

    def test_payment_total_calculated_correctly(self):
        """Test that payment total is calculated from ticket count and price."""
        # Add a guest
        Guest.objects.create(
            firstname='Guest',
            surname='One',
            email='guest@example.com',
            event_reservation=self.reservation,
        )
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        # 2 tickets (reservant + 1 guest) * 20 EUR = 40 EUR
        self.assertEqual(payment.total, Decimal('40.00'))

    def test_payment_total_with_custom_price(self):
        """Test that payment total uses custom price when set."""
        Guest.objects.create(
            firstname='Guest',
            surname='One',
            email='guest@example.com',
            event_reservation=self.reservation,
        )
        payment = ReservationPayment.from_reservation(self.reservation, variant='paypal')
        payment.custom_ticket_price = Decimal('25.00')
        payment.total = self.reservation.ticket_count() * payment.ticket_price
        # 2 tickets * 25 EUR = 50 EUR
        self.assertEqual(payment.total, Decimal('50.00'))


class GuestAndTicketCountTest(TestCase):
    """Tests for Guest model and ticket counting."""

    def setUp(self):
        """Create show, event, and person for testing."""
        self.show = Show.objects.create(
            title='Guest Test Show',
            description='Test description',
            cast='Test cast',
            card_image=create_test_image(),
            private=False,
            ticket_price=Decimal('15.00'),
        )

        next_week = timezone.now() + timedelta(days=7)
        self.event = Event.objects.create(
            show=self.show,
            admission=next_week.replace(hour=19, minute=0),
            begin=next_week.replace(hour=20, minute=0),
            reservation_capacity=150,
        )

        self.person = Person.objects.create(
            firstname='Test',
            surname='Reservant',
            email='test@example.com',
        )

    def test_reservation_without_guests_has_one_ticket(self):
        """Test that a reservation without guests counts as 1 ticket."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        self.assertEqual(reservation.ticket_count(), 1)

    def test_reservation_with_one_guest_has_two_tickets(self):
        """Test that a reservation with one guest counts as 2 tickets."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        Guest.objects.create(
            firstname='Guest',
            surname='One',
            event_reservation=reservation,
        )
        self.assertEqual(reservation.ticket_count(), 2)

    def test_reservation_with_multiple_guests(self):
        """Test ticket count with multiple guests."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        for i in range(5):
            Guest.objects.create(
                firstname=f'Guest{i}',
                surname='Test',
                event_reservation=reservation,
            )
        self.assertEqual(reservation.ticket_count(), 6)

    def test_guests_method_returns_all_guests(self):
        """Test that reservation.guests() returns all associated guests."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        guest1 = Guest.objects.create(
            firstname='Alice',
            surname='Test',
            event_reservation=reservation,
        )
        guest2 = Guest.objects.create(
            firstname='Bob',
            surname='Test',
            event_reservation=reservation,
        )
        guests = list(reservation.guests())
        self.assertEqual(len(guests), 2)
        self.assertIn(guest1, guests)
        self.assertIn(guest2, guests)

    def test_deleting_reservation_deletes_guests(self):
        """Test that deleting a reservation cascades to delete guests."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        Guest.objects.create(
            firstname='Guest',
            surname='Test',
            event_reservation=reservation,
        )
        reservation_id = reservation.id
        reservation.delete()
        # Guests should be deleted due to CASCADE
        self.assertEqual(Guest.objects.filter(event_reservation_id=reservation_id).count(), 0)

    def test_guest_inherits_from_person(self):
        """Test that Guest model inherits Person fields."""
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=self.person,
        )
        guest = Guest.objects.create(
            firstname='Test',
            surname='Guest',
            email='guest@example.com',
            street='Guest Street 123',
            zipcode=12345,
            town='Guest Town',
            phonenumber='+49123456789',
            event_reservation=reservation,
        )
        self.assertEqual(guest.firstname, 'Test')
        self.assertEqual(guest.surname, 'Guest')
        self.assertEqual(guest.email, 'guest@example.com')
        self.assertEqual(guest.street, 'Guest Street 123')

    def test_event_reservation_count(self):
        """Test that event.reservation_count() returns correct count."""
        # Create multiple reservations with payments
        for i in range(3):
            person = Person.objects.create(
                firstname=f'Person{i}',
                surname='Test',
                email=f'person{i}@example.com',
            )
            reservation = Reservation.objects.create(
                event=self.event,
                reservant=person,
            )
            # Add some guests to each reservation
            for j in range(i):
                Guest.objects.create(
                    firstname=f'Guest{j}',
                    surname=f'Of{i}',
                    event_reservation=reservation,
                )
            # Create payment to make reservation count
            payment = ReservationPayment.from_reservation(reservation, variant='paypal')
            payment.save()

        # 3 reservants + (0 + 1 + 2) guests = 6 total
        self.assertEqual(self.event.reservation_count(), 6)

    def test_event_reserved_tickets_display(self):
        """Test that event.reserved_tickets() returns correct format."""
        person = Person.objects.create(
            firstname='Test',
            surname='Person',
            email='test@example.com',
        )
        reservation = Reservation.objects.create(
            event=self.event,
            reservant=person,
        )
        Guest.objects.create(
            firstname='Guest',
            surname='Test',
            event_reservation=reservation,
        )
        payment = ReservationPayment.from_reservation(reservation, variant='paypal')
        payment.save()

        # 2 tickets (1 reservant + 1 guest) out of 150 capacity
        self.assertEqual(self.event.reserved_tickets(), '2/150')


class GuestTicketIdTest(TestCase):
    """Tests for the new ticket_id and checked_in fields on Guest."""

    def setUp(self):
        show = Show.objects.create(
            title='Test Show', description='', cast='',
            card_image=create_test_image(), private=False, ticket_price=Decimal('15.00'),
        )
        next_week = timezone.now() + timedelta(days=7)
        self.event = Event.objects.create(
            show=show,
            admission=next_week.replace(hour=19, minute=0),
            begin=next_week.replace(hour=20, minute=0),
            reservation_capacity=100,
        )
        self.person = Person.objects.create(firstname='Test', surname='User', email='t@example.com')
        self.reservation = Reservation.objects.create(event=self.event, reservant=self.person)

    def test_new_guest_gets_ticket_id(self):
        guest = Guest.objects.create(firstname='A', surname='B', event_reservation=self.reservation)
        self.assertIsNotNone(guest.ticket_id)

    def test_new_guest_checked_in_defaults_false(self):
        guest = Guest.objects.create(firstname='A', surname='B', event_reservation=self.reservation)
        self.assertFalse(guest.checked_in)

    def test_ticket_ids_are_unique_across_guests(self):
        g1 = Guest.objects.create(firstname='A', surname='B', event_reservation=self.reservation)
        g2 = Guest.objects.create(firstname='C', surname='D', event_reservation=self.reservation)
        self.assertNotEqual(g1.ticket_id, g2.ticket_id)

    def test_guest_with_null_ticket_id_allowed(self):
        # Old guests migrated without a ticket_id should still be valid
        guest = Guest.objects.create(firstname='Old', surname='Guest', event_reservation=self.reservation)
        guest.ticket_id = None
        guest.save()
        guest.refresh_from_db()
        self.assertIsNone(guest.ticket_id)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SendConfirmationMailPDFTest(TestCase):
    """Tests for the PDF generation in send_confirmation_mail()."""

    def setUp(self):
        from django.core import mail
        self.mail_outbox = mail.outbox

        show = Show.objects.create(
            title='PDF Test Show', description='', cast='',
            card_image=create_test_image(), private=False, ticket_price=Decimal('15.00'),
        )
        next_week = timezone.now() + timedelta(days=7)
        self.event = Event.objects.create(
            show=show,
            admission=next_week.replace(hour=19, minute=0),
            begin=next_week.replace(hour=20, minute=0),
            reservation_capacity=100,
        )
        self.person = Person.objects.create(
            firstname='Test', surname='User', email='test@example.com'
        )
        self.reservation = Reservation.objects.create(event=self.event, reservant=self.person)

    def _sent_email(self):
        from django.core import mail
        return mail.outbox[-1]

    def test_email_has_pdf_attachment(self):
        self.reservation.send_confirmation_mail()
        email = self._sent_email()
        self.assertEqual(len(email.attachments), 1)
        filename, content, mimetype = email.attachments[0]
        self.assertEqual(mimetype, 'application/pdf')
        self.assertIn(str(self.reservation.id), filename)
        self.assertTrue(filename.endswith('.pdf'))

    def test_no_png_attachments(self):
        self.reservation.send_confirmation_mail()
        email = self._sent_email()
        for filename, _, mimetype in email.attachments:
            self.assertNotEqual(mimetype, 'image/png')

    def test_pdf_is_non_empty(self):
        self.reservation.send_confirmation_mail()
        _, content, _ = self._sent_email().attachments[0]
        self.assertGreater(len(content), 0)
        self.assertTrue(content[:4] == b'%PDF', "Attachment should be a PDF")

    def test_solo_reservation_sends_one_page_pdf(self):
        """Reservant-only booking: PDF should have exactly 1 page."""
        self.reservation.send_confirmation_mail()
        _, content, _ = self._sent_email().attachments[0]
        # Each page object has /Type /Page; the parent dict has /Type /Pages (plural)
        page_count = content.count(b'/Type /Page\n')
        self.assertEqual(page_count, 1)

    def test_reservation_with_guests_sends_multi_page_pdf(self):
        """Reservant + 2 guests: PDF should have 3 pages."""
        Guest.objects.create(firstname='Alice', surname='A', event_reservation=self.reservation)
        Guest.objects.create(firstname='Bob', surname='B', event_reservation=self.reservation)
        self.reservation.send_confirmation_mail()
        _, content, _ = self._sent_email().attachments[0]
        page_count = content.count(b'/Type /Page\n')
        self.assertEqual(page_count, 3)

    def test_guest_with_null_ticket_id_excluded_from_pdf(self):
        """Old guests (ticket_id=None) should be skipped in the PDF."""
        g = Guest.objects.create(firstname='Old', surname='Guest', event_reservation=self.reservation)
        g.ticket_id = None
        g.save()
        self.reservation.send_confirmation_mail()
        _, content, _ = self._sent_email().attachments[0]
        # Only reservant page — old guest excluded
        page_count = content.count(b'/Type /Page\n')
        self.assertEqual(page_count, 1)

    def test_email_sent_to_reservant(self):
        self.reservation.send_confirmation_mail()
        email = self._sent_email()
        self.assertIn('test@example.com', email.to)

    def test_email_body_contains_german_sharing_instruction(self):
        self.reservation.send_confirmation_mail()
        self.assertIn('leite bitte den jeweiligen QR-Code', self._sent_email().body)

    def test_email_body_contains_english_sharing_instruction(self):
        self.reservation.send_confirmation_mail()
        self.assertIn('forward the relevant QR code to your guests', self._sent_email().body)


class CheckInViewTest(TestCase):
    """Tests for the check_in view — reservation UUID and guest ticket_id lookup."""

    def setUp(self):
        self.staff = User.objects.create_user('staff', password='pass', is_staff=True)
        self.client.force_login(self.staff)

        show = Show.objects.create(
            title='Check-in Show', description='', cast='',
            card_image=create_test_image(), private=False, ticket_price=Decimal('15.00'),
        )
        next_week = timezone.now() + timedelta(days=7)
        self.event = Event.objects.create(
            show=show,
            admission=next_week.replace(hour=19, minute=0),
            begin=next_week.replace(hour=20, minute=0),
            reservation_capacity=100,
        )
        self.person = Person.objects.create(firstname='Test', surname='User', email='t@example.com')
        self.reservation = Reservation.objects.create(event=self.event, reservant=self.person)
        self.guest = Guest.objects.create(
            firstname='Guest', surname='One', event_reservation=self.reservation
        )

    def _url(self, ticket_id):
        return f'/qr-scanner/{ticket_id}/check-in'

    def test_check_in_by_reservation_id(self):
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.checked_in)

    def test_check_in_by_guest_ticket_id(self):
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.checked_in)

    def test_guest_check_in_does_not_affect_reservation(self):
        self.client.get(self._url(self.guest.ticket_id))
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.checked_in)

    def test_already_checked_in_reservation_returns_400(self):
        self.reservation.checked_in = True
        self.reservation.save()
        response = self.client.get(self._url(self.reservation.id))
        self.assertEqual(response.status_code, 400)
        self.assertIn('already checked in', response.json()['error'])

    def test_already_checked_in_guest_returns_400(self):
        self.guest.checked_in = True
        self.guest.save()
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertEqual(response.status_code, 400)
        self.assertIn('already checked in', response.json()['error'])

    def test_unknown_uuid_returns_404(self):
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_guest_with_null_ticket_id_not_findable(self):
        self.guest.ticket_id = None
        self.guest.save()
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_reservation_check_in_returns_is_group_true(self):
        response = self.client.get(self._url(self.reservation.id))
        self.assertTrue(response.json().get('is_group'))

    def test_guest_check_in_does_not_return_is_group(self):
        response = self.client.get(self._url(self.guest.ticket_id))
        self.assertNotIn('is_group', response.json())
