from .models import PageView
from .ranges import range_navigation_items, range_since, resolve_range


def _format_duration(duration) -> str:
    if duration is None:
        return "–"

    total_seconds = int(duration.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}m {seconds}s"


def dashboard_callback(request, context):
    """Injects the KPI cards and range switcher shown above the charts on the admin
    index/dashboard page.

    Registered via UNFOLD["DASHBOARD_CALLBACK"] in config/settings/unfold_config.py; consumed by
    templates/admin/index.html. The charts pull their own data independently (same selected
    range, read straight off the request) via the registered components in stats/components.py.
    """
    range_spec = resolve_range(request)
    since = range_since(range_spec)

    page_views = PageView.objects.all()
    if since:
        page_views = page_views.filter(entered_at__gte=since)
    human_views = page_views.exclude(device_type=PageView.DeviceChoices.BOT)

    context.update(
        {
            "range_options": range_navigation_items(request, active=range_spec),
            "kpis": [
                {
                    # a "visit" = one session, however many pages it looked at
                    "title": f"Total visits ({range_spec.label.lower()}, excluding bots)",
                    "metric": human_views.values("session_key").distinct().count(),
                },
                {
                    "title": f"Total page views ({range_spec.label.lower()}, excluding bots)",
                    "metric": human_views.count(),
                },
                {
                    "title": "Bounce rate",
                    "metric": f"{PageView.objects.bounce_rate(since=since)}%",
                },
                {
                    "title": "Avg. time on site",
                    "metric": _format_duration(PageView.objects.avg_time_on_site(since=since)),
                },
                {
                    "title": f"Bot views ({range_spec.label.lower()})",
                    "metric": page_views.filter(device_type=PageView.DeviceChoices.BOT).count(),
                },
            ],
            "visits_chart_title": f"Visits ({range_spec.label.lower()}, excluding bots)",
            "device_chart_title": f"Sessions by device ({range_spec.label.lower()})",
        }
    )
    return context
