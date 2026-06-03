from django.contrib import admin

from stats.models import SiteStats


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    list_display = ("deleted_visitors",)
