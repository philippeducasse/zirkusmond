from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import PopUpElement


class PopUpElementAdmin(ModelAdmin):
    list_display = ("title", "active", "position")


admin.site.register(PopUpElement, PopUpElementAdmin)
