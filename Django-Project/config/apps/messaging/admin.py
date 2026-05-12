from django.contrib import admin
from .models import Message, ActivityLog, UserRestriction, BroadcastRecipient, MessageRecipientGroup
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "sender", "receiver", "message_type", "receiver_type", "timestamp", "is_read", "is_deleted"]
    list_filter = ["message_type", "receiver_type", "is_read", "is_deleted", "timestamp"]
    search_fields = ["sender__username", "receiver__username", "content"]
    readonly_fields = ["timestamp", "deleted_at"]
    fieldsets = (
        ("Message Info", {"fields": ("sender", "receiver", "message_type", "receiver_type")}),
        ("Content", {"fields": ("content", "parent_message")}),
        ("Broadcast", {"fields": ("department", "is_broadcast_optimized")}),
        ("Status", {"fields": ("is_read", "timestamp")}),
        ("Soft Delete", {"fields": ("is_deleted", "deleted_at", "deleted_by")}),
        ("Metadata", {"fields": ("created_via", "metadata")}),
    )
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "action_type", "target_user", "created_at", "ip_address"]
    list_filter = ["action_type", "created_at"]
    search_fields = ["user__username", "target_user__username", "metadata"]
    readonly_fields = ["created_at", "ip_address"]
    fieldsets = (
        ("User Info", {"fields": ("user", "target_user")}),
        ("Action", {"fields": ("action_type", "message")}),
        ("Request Info", {"fields": ("ip_address", "user_agent", "status_code")}),
        ("Values", {"fields": ("old_value", "new_value")}),
        ("Metadata", {"fields": ("metadata", "created_at", "timestamp_range")}),
    )
@admin.register(UserRestriction)
class UserRestrictionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "restriction_type", "is_active", "created_at", "expires_at"]
    list_filter = ["restriction_type", "is_active", "created_at"]
    search_fields = ["user__username", "reason"]
    readonly_fields = ["created_at"]
    fieldsets = (
        ("User & Admin", {"fields": ("user", "restricted_by")}),
        ("Restriction", {"fields": ("restriction_type", "reason")}),
        ("Permissions", {"fields": ("can_send_messages", "can_receive_broadcasts")}),
        ("Timeline", {"fields": ("created_at", "expires_at", "is_active")}),
    )
@admin.register(BroadcastRecipient)
class BroadcastRecipientAdmin(admin.ModelAdmin):
    list_display = ["id", "message", "recipient", "receiver_type", "is_delivered", "is_read", "delivery_timestamp"]
    list_filter = ["receiver_type", "is_delivered", "is_read", "delivery_timestamp"]
    search_fields = ["message__content", "recipient__username"]
    readonly_fields = ["delivery_timestamp"]
    fieldsets = (
        ("Message & Recipient", {"fields": ("message", "recipient", "receiver_type")}),
        ("Delivery", {"fields": ("is_delivered", "delivery_error", "delivery_timestamp")}),
        ("Read Status", {"fields": ("is_read", "read_at")}),
    )
@admin.register(MessageRecipientGroup)
class MessageRecipientGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "message", "recipient_type", "status", "total_recipients", "delivered_count", "failed_count"]
    list_filter = ["status", "recipient_type", "started_at"]
    search_fields = ["message__content", "department"]
    readonly_fields = ["started_at", "completed_at", "delivery_success_rate"]
    fieldsets = (
        ("Message & Recipients", {"fields": ("message", "recipient_type", "department")}),
        ("Counts", {"fields": ("total_recipients", "delivered_count", "failed_count", "delivery_success_rate")}),
        ("Status", {"fields": ("status", "started_at", "completed_at")}),
        ("Errors", {"fields": ("error_log",)}),
    )
