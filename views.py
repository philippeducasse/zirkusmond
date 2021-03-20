from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
# from django import forms
from django.views.generic.edit import CreateView


from .events.models import Show
from .zm.models import Visitor


def plain(request):
    ''' Give em our index, without doing much
    '''
    us = Show.objects.all()
    print(request.META.keys())
    v = Visitor(useragent=request.META['HTTP_USER_AGENT'],
                ip=request.META['REMOTE_ADDR'],
                referer=request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META.keys() else '')
    v.save()
    return render(request, 'index.html',
                  {'upcoming_shows': us})


def handle404(request, exception):
    '''
    '''
    return render(request, '404.html')


def server_error(request):
    return render(request, 'error_message.html',
                  {'error_code': 500,
                   'error_message': "Server Error"})


def permission_denied(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 403,
                   'error_message': "Permission Denied"})


def bad_request(request, exception):
    return render(request, 'error_message.html',
                  {'error_code': 400,
                   'error_message': "Bad Request"})
