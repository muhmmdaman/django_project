"""Utility functions for messaging system.
Provides helper functions for activity logging, message permissions, and user restrictions.
"""
from django.utils import timezone
from django.db.models import Q
from .models import ActivityLog, UserRestriction, Message
from accounts.models import CustomUser
def get_client_ip(request):
    """Get the client's IP address from the request.
    Handles X-Forwarded-For headers for proxied requests.
    Args:
        request: Django request object
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
def log_activity(
    user,
    action_type,
    target_user=None,
    message=None,
    ip_address=None,
    user_agent=None,
    metadata=None,
):
    """Log user activity to the ActivityLog model.
    Args:
        user (CustomUser): The user performing the action
        action_type (str): Type of action being logged
        target_user (CustomUser, optional): User who is the target of the action
        message (Message, optional): Message involved in the action
        ip_address (str, optional): IP address of the request
        user_agent (str, optional): User agent string from request
        metadata (dict, optional): Additional metadata to store
    Returns:
        ActivityLog: The created activity log entry
    """
    if metadata is None:
        metadata = {}
    activity = ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        target_user=target_user,
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata,
    )
    return activity
def can_send_message(sender, receiver=None):
    """Check if a user is allowed to send a message.
    Args:
        sender (CustomUser): The user attempting to send the message
        receiver (CustomUser, optional): The recipient of the message
    Returns:
        tuple: (can_send: bool, reason: str)
            - can_send: True if message can be sent, False otherwise
            - reason: Explanation if message cannot be sent
    """
    active_restrictions = UserRestriction.objects.filter(user=sender, is_active=True)
    for restriction in active_restrictions:
        if restriction.is_expired():
            restriction.is_active = False
            restriction.save(update_fields=["is_active"])
            continue
        if not restriction.can_send_messages:
            if restriction.restriction_type == "muted":
                return (False, "You are muted and cannot send messages.")
            elif restriction.restriction_type == "banned":
                return (False, "You are banned and cannot send messages.")
            elif restriction.restriction_type == "blocked_by_admin":
                return (False, "You have been blocked by an administrator.")
    if receiver:
        pass
    return (True, "")
def can_view_message(user, message):
    """Check if a user has permission to view a message.
    Args:
        user (CustomUser): The user attempting to view the message
        message (Message): The message to view
    Returns:
        bool: True if user can view the message, False otherwise
    """
    if message.is_deleted:
        return user == message.deleted_by
    if message.sender == user:
        return True
    if message.receiver == user:
        return True
    if message.message_type == "broadcast":
        if message.receiver_type == "all_users":
            return True
        if message.receiver_type == "department":
            if (
                hasattr(user, "student")
                and user.student.department == message.department
            ):
                return True
        from .models import BroadcastRecipient
        if BroadcastRecipient.objects.filter(message=message, recipient=user).exists():
            return True
    if user.role == "admin" or user.is_staff or user.is_superuser:
        return True
    return False
def get_user_restrictions(user):
    """Get all active restrictions for a user.
    Automatically deactivates expired restrictions.
    Args:
        user (CustomUser): The user to check restrictions for
    Returns:
        QuerySet: Active restrictions for the user
    """
    restrictions = UserRestriction.objects.filter(user=user, is_active=True)
    for restriction in restrictions:
        restriction.deactivate_if_expired()
    return UserRestriction.objects.filter(user=user, is_active=True)
def deactivate_expired_restrictions():
    """Deactivate all expired restrictions in the system.
    Should be run periodically (e.g., as a scheduled task).
    Returns:
        int: Number of restrictions that were deactivated
    """
    expired_restrictions = UserRestriction.objects.filter(
        is_active=True, expires_at__lt=timezone.now()
    ).exclude(expires_at__isnull=True)
    count = expired_restrictions.count()
    expired_restrictions.update(is_active=False)
    return count
