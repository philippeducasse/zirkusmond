from django.shortcuts import render

#from .models import Article


def plain(request):
    '''Give em our index, without doing much
    '''
    return render(request, 'html_head.html')
