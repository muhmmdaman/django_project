"""Management command to clean up expired restrictions and old activity logs.
Usage: python manage.py cleanup_restrictions
"""
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from messaging.models import ActivityLog, UserRestriction
logger = logging.getLogger("messaging")
class Command(BaseCommand):
    help = "Clean up expired restrictions and old activity logs"
    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Number of days to keep activity logs (default: 90)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting cleanup task..."))
        dry_run = options.get("dry_run", False)
        max_activity_days = options.get("days", 90)
        expired_count = self._deactivate_expired_restrictions(dry_run)
        deleted_count = self._delete_old_activity_logs(max_activity_days, dry_run)
        updated_count = self._update_user_restrictions_cache()
        self._log_cleanup_activity(expired_count, deleted_count, updated_count)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Cleanup complete!"
                f"\n  - Deactivated {expired_count} expired restrictions"
                f"\n  - Deleted {deleted_count} old activity logs"
                f"\n  - Updated {updated_count} user restriction caches"
                f'\n  - Mode: {"DRY RUN" if dry_run else "LIVE"}'
            )
        )
    def _deactivate_expired_restrictions(self, dry_run=False):
        now = timezone.now()
        expired_restrictions = UserRestriction.objects.filter(
            is_active=True, expires_at__lt=now
        )
        count = expired_restrictions.count()
        if count > 0:
            self.stdout.write(self.style.WARNING(f"Found {count} expired restrictions"))
            if not dry_run:
                expired_restrictions.update(is_active=False)
                logger.info(f"Deactivated {count} expired restrictions")
        return count
    def _delete_old_activity_logs(self, max_days=90, dry_run=False):
        cutoff_date = timezone.now() - timedelta(days=max_days)
        old_logs = ActivityLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        if count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {count} activity logs older than {max_days} days"
                )
            )
            if not dry_run:
                deleted_count, _ = old_logs.delete()
                logger.info(
                    f"Deleted {deleted_count} activity logs older than {max_days} days"
                )
        return count
    def _update_user_restrictions_cache(self):
        users_with_restrictions = CustomUser.objects.filter(
            restrictions__is_active=True
        ).distinct()
        count = 0
        for user in users_with_restrictions:
            if user.set_restricted_status():
                count += 1
        if count > 0:
            logger.info(f"Updated restriction cache for {count} users")
        return count
    def _log_cleanup_activity(self, expired_count, deleted_count, updated_count):
        admin_user = CustomUser.objects.filter(is_staff=True).first()
        if admin_user:
            metadata = {
                "expired_restrictions_deactivated": expired_count,
                "old_activity_logs_deleted": deleted_count,
                "user_caches_updated": updated_count,
            }
            ActivityLog.objects.create(
                user=admin_user,
                action_type="cleanup",
                metadata=metadata,
            )
