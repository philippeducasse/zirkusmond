from dataclasses import dataclass
from datetime import timedelta

from django.db.models.functions import TruncDate, TruncHour, TruncMonth
from django.http import HttpRequest
from django.utils import timezone

from .models import PageView

QUERY_PARAM = "range"


@dataclass(frozen=True)
class RangeSpec:
    key: str
    label: str
    days: int | None  # trailing window size; None means all-time
    trunc: type  # a django.db.models.functions Trunc* class -- how to bucket for the chart
    bucket_format: str  # strftime format for the chart's x-axis labels


RANGES = [
    RangeSpec("day", "Last 24 hours", 1, TruncHour, "%H:%M"),
    RangeSpec("week", "Last 7 days", 7, TruncDate, "%d.%m"),
    RangeSpec("month", "Last 30 days", 30, TruncDate, "%d.%m"),
    RangeSpec("year", "Last 12 months", 365, TruncMonth, "%b %Y"),
    RangeSpec("all", "All time", None, TruncMonth, "%b %Y"),
]
RANGES_BY_KEY = {spec.key: spec for spec in RANGES}
DEFAULT_RANGE_KEY = "day"


def resolve_range(request: HttpRequest) -> RangeSpec:
    key = request.GET.get(QUERY_PARAM, DEFAULT_RANGE_KEY)
    return RANGES_BY_KEY.get(key, RANGES_BY_KEY[DEFAULT_RANGE_KEY])


def range_since(range_spec: RangeSpec):
    """Start of the window, or None for all-time (no lower bound)."""
    if range_spec.days is None:
        return None
    return timezone.now() - timedelta(days=range_spec.days)


def range_navigation_items(request: HttpRequest, active: RangeSpec) -> list[dict]:
    """items= for unfold/components/navigation.html, preserving the rest of the querystring."""
    params = request.GET.copy()
    items = []
    for spec in RANGES:
        params[QUERY_PARAM] = spec.key
        items.append(
            {
                "title": spec.label,
                "link": f"?{params.urlencode()}",
                "active": spec.key == active.key,
            }
        )
    return items


def range_bucket_labels(range_spec: RangeSpec, since) -> list:
    """The ordered, zero-filled bucket keys a chart should plot -- same alignment Trunc*
    uses (the current timezone), so they line up with PageViewManager.views_per_bucket()'s
    keys even for buckets with no page views.
    """
    now = timezone.localtime()

    if since is None:
        earliest = (
            PageView.objects.order_by("entered_at").values_list("entered_at", flat=True).first()
        )
        start = timezone.localtime(earliest) if earliest else now
    else:
        start = timezone.localtime(since)

    if range_spec.trunc is TruncHour:
        hourly_buckets = []
        cursor = start.replace(minute=0, second=0, microsecond=0)
        while cursor <= now:
            hourly_buckets.append(cursor)
            cursor += timedelta(hours=1)
        return hourly_buckets

    if range_spec.trunc is TruncDate:
        daily_buckets = []
        day_cursor = start.date()
        end_day = now.date()
        while day_cursor <= end_day:
            daily_buckets.append(day_cursor)
            day_cursor += timedelta(days=1)
        return daily_buckets

    # TruncMonth
    monthly_buckets = []
    month_cursor = start.date().replace(day=1)
    end_month = now.date().replace(day=1)
    while month_cursor <= end_month:
        monthly_buckets.append(month_cursor)
        month, year = (month_cursor.month % 12) + 1, month_cursor.year
        if month_cursor.month == 12:
            year += 1
        month_cursor = month_cursor.replace(year=year, month=month)

    return monthly_buckets
