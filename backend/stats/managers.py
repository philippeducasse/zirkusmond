from django.db import models


class PageViewManager(models.Manager):
    def bounce_rate(self, since=None):
        qs = self.get_queryset()
        if since:
            qs = qs.filter(entered_at__gte=since)

        sessions = qs.values("session_key").annotate(views=models.Count("id"))

        total = sessions.count()

        if not total:
            return 0.0

        bounced = sessions.filter(views=1).count()
        return round(bounced / total * 100, 2)

    def avg_time_on_site(self, since=None):
        qs = self.get_queryset().filter(left_at__isnull=False)

        if since:
            qs = qs.filter(entered_at__gte=since)

        result = qs.annotate(duration=models.F("left_at") - models.F("entered_at")).aggregate(
            avg=models.Avg("duration")
        )

        return result["avg"]
