import logging
from django.apps import AppConfig
from django.db.models.signals import post_save
logger = logging.getLogger("messaging")
class MessagingConfig(AppConfig):
    name = "messaging"
    default_auto_field = "django.db.models.BigAutoField"
    def ready(self):
        from accounts.models import CustomUser
        from messaging.models import ActivityLog, Message, UserRestriction
        post_save.connect(
            self._on_message_created,
            sender=Message,
            dispatch_uid="messaging_update_last_activity",
        )
        post_save.connect(
            self._on_restriction_changed,
            sender=UserRestriction,
            dispatch_uid="messaging_update_is_restricted",
        )
    @staticmethod
    def _on_message_created(sender, instance, created, **kwargs):
        if created:
            from accounts.models import CustomUser
            from django.utils import timezone
            try:
                sender_obj = instance.sender
                sender_obj.last_activity = timezone.now()
                sender_obj.save(update_fields=["last_activity"])
                logger.info(
                    f"Message created: {instance.id} by {sender_obj.username} "
                    f"- Type: {instance.message_type}, "
                    f"Via: {instance.created_via}"
                )
            except Exception as e:
                logger.error(f"Error updating last_activity: {str(e)}")
    @staticmethod
    def _on_restriction_changed(sender, instance, created, **kwargs):
        try:
            user = instance.user
            had_restrictions = user.is_restricted
            user.set_restricted_status()
            if created:
                logger.info(
                    f"Restriction created for user {user.username}: "
                    f"{instance.get_restriction_type_display()} - "
                    f"Reason: {instance.reason[:50]}..."
                )
            else:
                if had_restrictions and not user.is_restricted:
                    logger.info(f"Restriction deactivated for user {user.username}")
                elif not had_restrictions and user.is_restricted:
                    logger.info(f"Restriction activated for user {user.username}")
        except Exception as e:
            logger.error(f"Error updating is_restricted: {str(e)}")
