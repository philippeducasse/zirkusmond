from django.db.models import Model
from rest_framework.serializers import ModelSerializer


def homepage_element_serializer(model: type[Model]) -> type[ModelSerializer]:
    """Build a ModelSerializer for a concrete HomePageElement subclass.

    HomePageElement is abstract, so each concrete element type (PopUpElement,
    and whatever gets added later) needs its own serializer. This factory
    derives one that exposes all of the subclass's fields.
    """
    meta = type("Meta", (), {"model": model, "fields": "__all__"})
    return type(f"{model.__name__}Serializer", (ModelSerializer,), {"Meta": meta})
