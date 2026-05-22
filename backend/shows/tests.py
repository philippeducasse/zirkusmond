from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from events.models import Event
from shows.models import PastShow, Show, UnscheduledShow, UpcomingShow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_image():
    buf = BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')


def make_show(**kwargs):
    defaults = dict(title='Test Show', description='A description', cast='A cast',
                    card_image=make_image(), private=False)
    defaults.update(kwargs)
    return Show.objects.create(**defaults)


def make_event(show, offset_days=7):
    base = timezone.now() + timedelta(days=offset_days)
    return Event.objects.create(
        show=show,
        admission=base.replace(hour=19, minute=0, second=0, microsecond=0),
        begin=base.replace(hour=20, minute=0, second=0, microsecond=0),
        reservation_capacity=150,
        open_for_reservation=True,
    )


# ---------------------------------------------------------------------------
# Show model
# ---------------------------------------------------------------------------

class ShowModelTest(TestCase):
    def setUp(self):
        self.show = make_show()

    def test_str_is_title(self):
        self.assertEqual(str(self.show), 'Test Show')

    def test_future_events_returns_upcoming(self):
        event = make_event(self.show, offset_days=5)
        self.assertIn(event, self.show.future_events())

    def test_future_events_excludes_past(self):
        past = make_event(self.show, offset_days=-1)
        self.assertNotIn(past, self.show.future_events())

    def test_last_event_returns_latest(self):
        make_event(self.show, offset_days=3)
        later = make_event(self.show, offset_days=10)
        self.assertEqual(self.show.last_event(), later)

    def test_first_event_returns_earliest(self):
        earlier = make_event(self.show, offset_days=3)
        make_event(self.show, offset_days=10)
        self.assertEqual(self.show.first_event(), earlier)

    def test_reservation_open_true_when_event_open(self):
        make_event(self.show)
        self.assertTrue(self.show.reservation_open())

    def test_reservation_open_false_with_no_events(self):
        self.assertFalse(self.show.reservation_open())

    def test_reservation_open_false_when_all_closed(self):
        make_event(self.show, offset_days=-1)
        self.assertFalse(self.show.reservation_open())

    def test_show_in_preview_true_for_public_with_future_event(self):
        make_event(self.show)
        self.assertTrue(self.show.show_in_preview())

    def test_show_in_preview_false_for_private_show(self):
        self.show.private = True
        self.show.save()
        make_event(self.show)
        self.assertFalse(self.show.show_in_preview())

    def test_show_in_preview_true_for_public_with_no_events(self):
        self.assertTrue(self.show.show_in_preview())

    def test_show_in_preview_false_when_last_event_long_past(self):
        make_event(self.show, offset_days=-2)
        self.assertFalse(self.show.show_in_preview())

    def test_dates_text_joins_future_events(self):
        make_event(self.show, offset_days=3)
        make_event(self.show, offset_days=10)
        result = self.show.dates_text()
        self.assertIn('/', result)

    def test_dates_text_empty_when_no_future_events(self):
        self.assertEqual(self.show.dates_text(), '')

    def test_lastmod_format(self):
        import re
        self.assertRegex(self.show.lastmod(), r'\d{4}-\d{2}-\d{2}')


# ---------------------------------------------------------------------------
# Show managers
# ---------------------------------------------------------------------------

class ShowManagerTest(TestCase):
    def setUp(self):
        self.upcoming_show = make_show(title='Upcoming')
        make_event(self.upcoming_show, offset_days=5)

        self.past_show = make_show(title='Past')
        make_event(self.past_show, offset_days=-5)

        self.unscheduled_show = make_show(title='Unscheduled')

    def test_upcoming_includes_shows_with_future_events(self):
        self.assertIn(self.upcoming_show, UpcomingShow.objects.all())

    def test_upcoming_excludes_past_only_shows(self):
        self.assertNotIn(self.past_show, UpcomingShow.objects.all())

    def test_upcoming_excludes_unscheduled(self):
        self.assertNotIn(self.unscheduled_show, UpcomingShow.objects.all())

    def test_past_includes_shows_with_only_past_events(self):
        self.assertIn(self.past_show, PastShow.objects.all())

    def test_past_excludes_upcoming(self):
        self.assertNotIn(self.upcoming_show, PastShow.objects.all())

    def test_unscheduled_includes_shows_with_no_events(self):
        self.assertIn(self.unscheduled_show, UnscheduledShow.objects.all())

    def test_unscheduled_excludes_shows_with_events(self):
        self.assertNotIn(self.upcoming_show, UnscheduledShow.objects.all())
        self.assertNotIn(self.past_show, UnscheduledShow.objects.all())


# ---------------------------------------------------------------------------
# Show view
# ---------------------------------------------------------------------------

class ShowViewTest(TestCase):
    def setUp(self):
        self.show = make_show()

    def test_show_page_returns_200(self):
        response = self.client.get(f'/show/{self.show.pk}')
        self.assertEqual(response.status_code, 200)

    def test_show_in_context(self):
        response = self.client.get(f'/show/{self.show.pk}')
        self.assertEqual(response.context['show'], self.show)

    def test_nonexistent_show_returns_404(self):
        response = self.client.get('/show/99999')
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Site-wide views
# ---------------------------------------------------------------------------

class SiteViewsTest(TestCase):
    def test_home_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_with_upcoming_show(self):
        show = make_show()
        make_event(show)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(show, response.context['upcoming_shows'])

    def test_about_returns_200(self):
        self.assertEqual(self.client.get('/about').status_code, 200)

    def test_contact_returns_200(self):
        self.assertEqual(self.client.get('/contact').status_code, 200)

    def test_rentals_returns_200(self):
        self.assertEqual(self.client.get('/rentals').status_code, 200)

    def test_international_returns_200(self):
        self.assertEqual(self.client.get('/international').status_code, 200)

    def test_events_list_returns_200(self):
        self.assertEqual(self.client.get('/events').status_code, 200)

    def test_impressum_returns_200(self):
        self.assertEqual(self.client.get('/impressum').status_code, 200)

    def test_datenschutz_returns_200(self):
        self.assertEqual(self.client.get('/datenschutz').status_code, 200)

    def test_robots_txt_returns_200(self):
        self.assertEqual(self.client.get('/robots.txt').status_code, 200)

    def test_sitemap_returns_200(self):
        self.assertEqual(self.client.get('/sitemap.xml').status_code, 200)

    def test_newsletter_get_redirects(self):
        response = self.client.get('/newsletter_registration')
        self.assertEqual(response.status_code, 302)

    def test_newsletter_post_valid_email_shows_confirmation(self):
        response = self.client.post('/newsletter_registration', {'email': 'user@example.com'})
        self.assertEqual(response.status_code, 200)

    def test_newsletter_post_invalid_email_redirects(self):
        response = self.client.post('/newsletter_registration', {'email': 'not-an-email'})
        self.assertEqual(response.status_code, 302)
