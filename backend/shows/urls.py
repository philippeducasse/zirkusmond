from django.urls import path

from shows import views

urlpatterns = [
    path("show/<int:show_id>", views.show, name="show"),
]
