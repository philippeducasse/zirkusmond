from django.urls import path

from shows import views

urlpatterns = [
    path("shows/<int:show_id>", views.get_show, name="show_detail"),
]