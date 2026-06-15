from django.contrib import admin
from unfold.admin import ModelAdmin

from stats.models import SiteStats


@admin.register(SiteStats)
class SiteStatsAdmin(ModelAdmin):
    list_display = ("deleted_visitors",)
