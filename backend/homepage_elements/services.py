from .models import HomePageElement
from .serializers import homepage_element_serializer


def get_active_homepage_elements() -> list[dict]:
    """Serialized payload for every active concrete HomePageElement.

    Each entry carries a ``type`` discriminator (the model name) so the
    frontend can tell the element kinds apart.
    """
    elements: list[dict] = []
    for subclass in HomePageElement.__subclasses__():
        serializer = homepage_element_serializer(subclass)
        for element in subclass.objects.filter(active=True):
            elements.append({**serializer(element).data, "type": subclass._meta.model_name})

    return elements
