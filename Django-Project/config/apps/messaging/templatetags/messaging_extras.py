from django import template
from django.utils import timezone
from datetime import timedelta
register = template.Library()
@register.filter
def relative_time(value):
    if not value:
        return ""
    now = timezone.now()
    diff = now - value
    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins} min{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 172800:
        return "Yesterday"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} days ago"
    else:
        return value.strftime("%b %d, %Y")
@register.filter
def is_broadcast(message):
    return message.message_type == "broadcast"
