from django.urls import path

from newsletter import views

urlpatterns = [
    # API endpoint
    path(
        "register",
        views.register,
    ),
    # Template view (deprecated, will be removed after migration)
    path(
        "newsletter-registration",
        views.newsletter_registration,
    ),
]
