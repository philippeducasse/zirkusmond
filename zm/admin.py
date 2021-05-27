from django.contrib import admin
from .models import Visitor

class VisitorAdmin(admin.ModelAdmin):
    list_display =('ip', 'useragent', 'referer', 'time')
    list_filter = ('time', )

# Register your models here.
admin.site.register(Visitor, VisitorAdmin)
