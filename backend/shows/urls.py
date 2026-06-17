from django.urls import path

from shows import views

urlpatterns = [
    # Template view (deprecated, will be removed after migration)
    path("show/<int:show_id>", views.show, name="show"),
    # API endpoint
    path("shows/<int:show_id>", views.get_show, name="show_detail"),
]
