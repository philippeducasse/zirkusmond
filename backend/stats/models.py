from django.db import models


class SiteStats(models.Model):
    deleted_visitors = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"Site Stats (deleted_visitors={self.deleted_visitors})"
