from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include

from django.conf import settings
from django.conf.urls.static import static

import views
from events import views as event_views
from reservations import views as reservation_views
from events.views_admin import purge_old_payments_view
from shows import views as show_views

urlpatterns = [
    path('mondmin/', admin.site.urls),
    path("mondmin/events/", include("events.urls", namespace="events_admin")),
    path("mondmin-purge-old-payments", purge_old_payments_view),
    path('tinymce/', include('tinymce.urls')),

    path('', views.plain),
    path('events', views.event_list),
    path('about', views.about),
    path('contact', views.contact),
    path('rentals', views.rentals),
    path('international', views.international),
    path('newsletter_registration', views.newsletter_registration),
    re_path('^impressum.*', views.impressum),
    re_path('^datenschutz.*', views.datenschutz),
    path('robots.txt', views.robots),
    path('sitemap.xml', views.sitemap),
    path('show/<int:show_id>', show_views.show, name='show'),
    path('reserve/<int:show_id>', reservation_views.reserve, name='reserve'),
    path('reservation_status/<uuid:payment_id>', reservation_views.reservation_status),
    path('payment/<uuid:payment_id>', reservation_views.payment, name='payment'),
    path('payment-success/<uuid:payment_id>', reservation_views.payment_success),
    path('payment-failure/<uuid:payment_id>', reservation_views.payment_fail),
    path('payment/<uuid:payment_id>/<str:payment_variant>', reservation_views.payment,
         name='payment'),

    path('qr-scanner/get-events', reservation_views.get_events),
    path('qr-scanner/', reservation_views.qr_scanner),
    path('qr-scanner/<uuid:reservation_id>/check-in', reservation_views.check_in),

    path('payments/', include('payments.urls')),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,
                                       document_root=settings.MEDIA_ROOT)

handler404 = views.handle404
handler500 = views.server_error
handler403 = views.permission_denied
handler400 = views.bad_request
