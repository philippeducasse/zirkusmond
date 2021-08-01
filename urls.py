"""zirkusmond URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from django.conf import settings
from django.conf.urls.static import static

from . import views
from .events import views as event_views
from .gallery import views as gviews


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.plain),
    path('newsletter_registration', views.newsletter_registration),
    url(r'^impressum.*', views.impressum),
    url(r'.*robots.txt', views.robots),
    path('sitemap.xml', views.sitemap),
    path('show/<int:show_id>', event_views.show, name='show'),
    path('reserve/<int:show_id>', event_views.reserve, name='reserve'),
    path('reservation_status/<uuid:payment_id>', event_views.reservation_status),
    path('payment/<uuid:payment_id>', event_views.payment, name='payment'),
    path('payment-success/<uuid:payment_id>', event_views.payment_success),
    path('payment-failure/<uuid:payment_id>', event_views.payment_fail),
    path('payment/<uuid:payment_id>/<str:payment_variant>', event_views.payment,
         name='payment'),


    path('gallery', gviews.gallery, name='gallery'),
    path('gallery/<int:pk>', gviews.album),
    path('gallery/<int:album_id>/<int:foto_id>', gviews.foto),

    url(r'^markdownx/', include('markdownx.urls')),
    path('payments/', include('payments.urls')),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,
                                       document_root=settings.MEDIA_ROOT)

handler404 = views.handle404
handler500 = views.server_error
handler403 = views.permission_denied
handler400 = views.bad_request
