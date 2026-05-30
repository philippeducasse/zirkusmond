from django.contrib import admin
from django.utils.html import format_html

from stats.models import SiteStats


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    list_display = ("deleted_visitors", "purge_link")

    def purge_link(self, obj):
        url = "/mondmin-purge-old-payments"
        return format_html('<a class="button" href="{}">Purge old payments</a>', url)

    purge_link.short_description = "Actions"
