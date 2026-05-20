from django.core.management.base import BaseCommand
from events.services import purge_old_payments

class Command(BaseCommand):
    help = "Delete ReservationPayments older than ~6 months and bump SiteStats.deleted_visitors."

    def add_arguments(self, parser):
        parser.add_argument("--confirmed-only", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        result = purge_old_payments(
            confirmed_only=opts["confirmed_only"],
            dry_run=opts["dry_run"],
        )
        if result["dry_run"]:
            self.stdout.write(self.style.NOTICE(
                f"[DRY-RUN] Found {result['payments_found']} payments before {result['cutoff']:%Y-%m-%d}; "
                f"visitors to add: {result['visitors_to_add']}."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Deleted {result['deleted_count']} payments; "
                f"+{result['visitors_to_add']} visitors accumulated. "
                f"deleted_visitors now {result['final_deleted_visitors']}."
            ))

