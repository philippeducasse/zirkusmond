from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Show, Event


admin.site.register(Show, MarkdownxModelAdmin)
admin.site.register(Event)
