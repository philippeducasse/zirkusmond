from django.urls import path

from .views import get_additional_elements

urlpatterns = [
    path(
        "homepage-elements",
        get_additional_elements,
    ),
]
