import datetime
import logging
from typing import Any

from django.db import transaction
from django.db.models import Exists, F, OuterRef
from django.utils import timezone

from reservations.models import Payment, Reservation
from stats.models import SiteStats

logger = logging.getLogger(__name__)

HALF_YEAR_DAYS = 220  # ≈6 months


def purge_old_payments(*, confirmed_only: bool = False, dry_run: bool = False) -> dict[str, Any]:
    cutoff = timezone.now() - datetime.timedelta(days=HALF_YEAR_DAYS)

    payments_qs = Payment.objects.filter(created_at__lt=cutoff)
    if confirmed_only:
        payments_qs = payments_qs.filter(status=Payment.Status.COMPLETED)

    payments = list(
        payments_qs.select_related(
            "reservation",
            "reservation__event",
            "reservation__event__show",
        )
    )

    total_visitors = 0
    for payment in payments:
        if payment.reservation:
            total_visitors += payment.reservation.ticket_count()

    if dry_run:
        return {
            "cutoff": cutoff,
            "payments_found": len(payments),
            "visitors_to_add": total_visitors,
            "deleted_count": 0,
            "final_deleted_visitors": None,
            "dry_run": True,
        }

    with transaction.atomic():
        stats, _ = SiteStats.objects.select_for_update().get_or_create(pk=1)
        SiteStats.objects.filter(pk=stats.pk).update(
            deleted_visitors=F("deleted_visitors") + total_visitors
        )
        deleted_count, _ = payments_qs.delete()
        stats.refresh_from_db()

    return {
        "cutoff": cutoff,
        "payments_found": len(payments),
        "visitors_to_add": total_visitors,
        "deleted_count": deleted_count,
        "final_deleted_visitors": stats.deleted_visitors,
        "dry_run": False,
    }


def purge_orphan_reservations(*, dry_run: bool = True) -> dict[str, Any]:
    orphan_reservations_qs = Reservation.objects.filter(
        ~Exists(Payment.objects.filter(reservation=OuterRef("pk")))
    )
    reservations_to_delete = orphan_reservations_qs.count()

    if dry_run:
        return {
            "dry_run": True,
            "reservations_to_delete": reservations_to_delete,
            "deleted_reservations": 0,
        }

    with transaction.atomic():
        deleted_reservations, _ = orphan_reservations_qs.delete()

    return {
        "dry_run": False,
        "reservations_to_delete": reservations_to_delete,
        "deleted_reservations": deleted_reservations,
    }
