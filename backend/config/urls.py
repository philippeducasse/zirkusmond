from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import config.views as views

urlpatterns = [
    # Admin
    path("mondmin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    # Static pages
    path("", views.homepage_api),
    # Apps
    path("", include("shows.urls")),
    path("", include("reservations.urls")),
    path("newsletter/", include("newsletter.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)