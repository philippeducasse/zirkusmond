from django.db.models import Count, Sum

from reservations.payments.models import Payment

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

    page_views = PageView.objects.filter(entered_at__gte=since)
    human_views = page_views.exclude(device_type=PageView.DeviceChoices.BOT)

    completed_payments = Payment.objects.filter(created_at__gte=since).filter(
        status=Payment.Status.COMPLETED
    )

    agg = completed_payments.aggregate(
        guest_count=Count("reservation__guests"),
        reservation_count=Count("reservation", distinct=True),
    )

    total_revenue = completed_payments.values("total").aggregate(revenue=Sum("total"))["revenue"]
    total_guests = agg["guest_count"] + agg["reservation_count"]

    context.update(
        {
            "range_options": range_navigation_items(request, active=range_spec),
            "kpis": [
                {
                    # a "visitor" = one session, however many pages it looked at
                    "title": "Visitors (excluding bots)",
                    "metric": human_views.values("session_key").distinct().count(),
                },
                {
                    "title": "Payments",
                    "metric": completed_payments.count(),
                },
                {
                    "title": "Revenue",
                    "metric": total_revenue,
                },
                {
                    "title": "Tickets sold",
                    "metric": total_guests,
                },
                {
                    "title": "Page views (excluding bots)",
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
                    "title": "Bot views",
                    "metric": page_views.filter(device_type=PageView.DeviceChoices.BOT).count(),
                },
            ],
            "visits_chart_title": "Visits, excluding bots)",
            "device_chart_title": "Sessions by device",
        }
    )
    return context
