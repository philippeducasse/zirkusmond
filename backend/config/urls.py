from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

import config.views as views

urlpatterns = [
    # Admin
    path("mondmin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    # Static pages
    # path("", views.homepage),
    path("", views.homepage_api),
    path("events", views.event_list),
    path("about", views.about),
    path("contact", views.contact),
    path("rentals", views.rentals),
    path("international", views.international),
    path("newsletter_registration", views.newsletter_registration),
    re_path("^impressum.*", views.impressum),
    re_path("^datenschutz.*", views.datenschutz),
    path("robots.txt", views.robots),
    path("sitemap.xml", views.sitemap),
    # Apps
    path("", include("shows.urls")),
    path("", include("reservations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.handle404
handler500 = views.server_error
handler403 = views.permission_denied
handler400 = views.bad_request
