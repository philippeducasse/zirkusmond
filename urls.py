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
from .gallery import views as gviews

handler404 = views.handle404

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.plain),
    path('show/<int:show_id>', views.show, name='show'),

    path('gallery', gviews.gallery, name='gallery'),
    path('gallery/<int:pk>', gviews.album),
    path('gallery/<int:album_id>/<int:foto_id>', gviews.foto),
    path('reserve/<int:show_id>', views.reserve, name='reserve'),
    path('event/<int:event_id>', views.event, name='event'),
    path('payment/<int:payment_id>', views.payment, name='payment'),
    path('payment-success/<int:payment_id>', views.payment_success),
    path('payment-failure/<int:payment_id>', views.payment_fail),
    path('payment/<int:payment_id>/<str:payment_variant>', views.payment, name='payment'),
    # TODO Opps response for payment

    url(r'^markdownx/', include('markdownx.urls')),
    path('payments/', include('payments.urls')),
]


if settings.DEBUG or True:  # TODO no actual http server deployment
    urlpatterns = urlpatterns + static(settings.MEDIA_URL,
                                       document_root=settings.MEDIA_ROOT)
