from django.urls import path

from newsletter import views

urlpatterns = [
    path(
        "register",
        views.register,
    ),
]
