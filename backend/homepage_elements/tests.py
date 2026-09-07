from django.test import TestCase
from rest_framework.test import APIClient

from homepage_elements.models import PopUpElement, PostShowsElement, PreShowsElement
from homepage_elements.services import get_active_homepage_elements


def _make(model, *, active=False, title="Element", link=""):
    return model.objects.create(
        title_de=f"{title} DE",
        title_en=f"{title} EN",
        message_de="<p>Nachricht</p>",
        message_en="<p>Message</p>",
        active=active,
        link=link,
    )


class OneActivePerTypeTest(TestCase):
    """`HomePageElement.save()` keeps at most one active row per concrete model."""

    def test_activating_one_deactivates_the_other_of_same_type(self) -> None:
        first = _make(PreShowsElement, active=True)
        second = _make(PreShowsElement, active=True)

        first.refresh_from_db()
        self.assertFalse(first.active)
        self.assertTrue(second.active)

    def test_reactivating_the_first_deactivates_the_second(self) -> None:
        first = _make(PreShowsElement, active=True)
        second = _make(PreShowsElement, active=True)

        first.active = True
        first.save()

        second.refresh_from_db()
        self.assertTrue(first.active)
        self.assertFalse(second.active)

    def test_other_element_types_are_not_affected(self) -> None:
        popup = _make(PopUpElement, active=True)
        pre = _make(PreShowsElement, active=True)
        post = _make(PostShowsElement, active=True)

        popup.refresh_from_db()
        pre.refresh_from_db()
        post.refresh_from_db()
        self.assertTrue(popup.active)
        self.assertTrue(pre.active)
        self.assertTrue(post.active)

    def test_saving_an_inactive_element_leaves_the_active_one_alone(self) -> None:
        active = _make(PreShowsElement, active=True)
        _make(PreShowsElement, active=False)

        active.refresh_from_db()
        self.assertTrue(active.active)


class GetActiveHomepageElementsTest(TestCase):
    def test_returns_empty_list_when_nothing_is_active(self) -> None:
        _make(PopUpElement, active=False)
        _make(PreShowsElement, active=False)

        self.assertEqual(get_active_homepage_elements(), [])

    def test_returns_only_active_elements(self) -> None:
        _make(PreShowsElement, active=True, title="Shown")
        _make(PreShowsElement, active=False, title="Hidden")

        elements = get_active_homepage_elements()

        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["title_en"], "Shown EN")

    def test_each_element_carries_its_model_name_as_type(self) -> None:
        _make(PopUpElement, active=True)
        _make(PreShowsElement, active=True)
        _make(PostShowsElement, active=True)

        types = {element["type"] for element in get_active_homepage_elements()}

        self.assertEqual(types, {"popupelement", "preshowselement", "postshowselement"})

    def test_serialized_payload_exposes_the_expected_fields(self) -> None:
        _make(PreShowsElement, active=True, link="https://example.com")

        (element,) = get_active_homepage_elements()

        self.assertEqual(
            set(element),
            {
                "id",
                "title_de",
                "title_en",
                "message_de",
                "message_en",
                "active",
                "link",
                "type",
            },
        )
        self.assertEqual(element["link"], "https://example.com")


class HomepageEndpointAdditionalElementsTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_additional_elements_reflect_active_rows(self) -> None:
        _make(PreShowsElement, active=True, title="Before")
        _make(PostShowsElement, active=False, title="After")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        additional = response.json()["additional_elements"]
        self.assertEqual(len(additional), 1)
        self.assertEqual(additional[0]["type"], "preshowselement")
        self.assertEqual(additional[0]["title_en"], "Before EN")

    def test_additional_elements_empty_when_no_active_rows(self) -> None:
        _make(PopUpElement, active=False)

        response = self.client.get("/")

        self.assertEqual(response.json()["additional_elements"], [])
