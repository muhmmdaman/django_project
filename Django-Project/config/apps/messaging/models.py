from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
class Message(models.Model):
    MESSAGE_TYPES = [
        ("private", "Private"),
        ("broadcast", "Broadcast"),
    ]
    RECEIVER_TYPES = [
        ("individual", "Individual"),
        ("department", "Department"),
        ("all_users", "All Users"),
        ("custom", "Custom List"),
    ]
    CREATED_VIA_CHOICES = [
        ("ui", "UI"),
        ("api", "API"),
        ("bulk_upload", "Bulk Upload"),
    ]
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="received_messages",
        null=True,
        blank=True,
        help_text="For individual messages only",
    )
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default="private"
    )
    department = models.CharField(
        max_length=10, null=True, blank=True, help_text="For broadcast messages only"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when message was read by recipient"
    )
    parent_message = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_messages",
    )
    receiver_type = models.CharField(
        max_length=20,
        choices=RECEIVER_TYPES,
        default="individual",
        help_text="Type of receiver for this message",
    )
    is_broadcast_optimized = models.BooleanField(
        default=False, help_text="True if this is an optimized broadcast message"
    )
    created_via = models.CharField(
        max_length=20,
        choices=CREATED_VIA_CHOICES,
        default="ui",
        help_text="Channel through which message was created",
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional metadata for the message"
    )
    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["sender", "-timestamp"]),
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["is_deleted"]),
        ]
    def __str__(self):
        if self.message_type == "broadcast":
            return f"Broadcast: {self.content[:50]} - {self.timestamp}"
        else:
            return f"{self.sender} → {self.receiver}: {self.content[:50]}"
    @property
    def is_soft_deleted(self):
        return self.is_deleted
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
    def soft_delete(self, deleted_by):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])
    def recover(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("message_sent", "Message Sent"),
        ("broadcast_sent", "Broadcast Sent"),
        ("department_message_sent", "Department Message Sent"),
        ("message_deleted", "Message Deleted"),
        ("message_recovered", "Message Recovered"),
        ("user_banned", "User Banned"),
        ("user_unbanned", "User Unbanned"),
        ("user_muted", "User Muted"),
        ("user_unmuted", "User Unmuted"),
        ("teacher_added", "Teacher Added"),
        ("teacher_updated", "Teacher Updated"),
        ("teacher_deleted", "Teacher Deleted"),
        ("teacher_salary_paid", "Teacher Salary Paid"),
        ("user_promoted_to_admin", "User Promoted to Admin"),
        ("user_demoted_from_admin", "User Demoted from Admin"),
    ]
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="activity_logs"
    )
    action_type = models.CharField(
        max_length=30, choices=ACTION_TYPES, help_text="Type of action performed"
    )
    target_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="target_activity_logs",
        help_text="User who is the target of the action",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp_range = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action_type", "-created_at"]),
            models.Index(fields=["target_user", "-created_at"]),
        ]
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} - {self.created_at}"
class UserRestriction(models.Model):
    RESTRICTION_TYPES = [
        ("banned", "Banned"),
        ("muted", "Muted"),
        ("blocked_by_admin", "Blocked By Admin"),
    ]
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="restrictions",
        help_text="User being restricted",
    )
    restriction_type = models.CharField(
        max_length=20, choices=RESTRICTION_TYPES, help_text="Type of restriction"
    )
    reason = models.TextField(help_text="Reason for restriction")
    restricted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="restrictions_created",
        help_text="Admin who created the restriction",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    can_receive_broadcasts = models.BooleanField(default=False)
    can_send_messages = models.BooleanField(default=False)
    class Meta:
        verbose_name = "User Restriction"
        verbose_name_plural = "User Restrictions"
        ordering = ["-created_at"]
        unique_together = [["user", "restriction_type"]]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["restriction_type", "is_active"]),
            models.Index(fields=["expires_at"]),
        ]
    def __str__(self):
        return f"{self.user} - {self.get_restriction_type_display()} - {'Active' if self.is_active else 'Inactive'}"
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    def deactivate_if_expired(self):
        if self.is_expired():
            self.is_active = False
            self.save(update_fields=["is_active"])
            return True
        return False
class BroadcastRecipient(models.Model):
    RECEIVER_TYPES = [
        ("individual_broadcast", "Individual Broadcast"),
        ("department_broadcast", "Department Broadcast"),
        ("global_broadcast", "Global Broadcast"),
        ("admin_broadcast", "Admin Broadcast"),
    ]
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="broadcast_recipients"
    )
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_broadcasts"
    )
    receiver_type = models.CharField(
        max_length=30, choices=RECEIVER_TYPES, help_text="Type of broadcast message"
    )
    is_delivered = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    delivery_error = models.TextField(null=True, blank=True)
    delivery_timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Broadcast Recipient"
        verbose_name_plural = "Broadcast Recipients"
        ordering = ["-delivery_timestamp"]
        unique_together = [["message", "recipient"]]
        indexes = [
            models.Index(fields=["message", "recipient"]),
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["is_delivered"]),
        ]
    def __str__(self):
        return (
            f"{self.message.id} → {self.recipient} ({self.get_receiver_type_display()})"
        )
class MessageRecipientGroup(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    RECIPIENT_TYPES = [
        ("department", "Department"),
        ("all_students", "All Students"),
        ("all_users", "All Users"),
        ("custom_list", "Custom List"),
    ]
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="recipient_groups"
    )
    recipient_type = models.CharField(
        max_length=20, choices=RECIPIENT_TYPES, help_text="Type of recipient group"
    )
    department = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Department filter if applicable",
    )
    total_recipients = models.IntegerField(
        help_text="Total number of recipients in group"
    )
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(null=True, blank=True)
    class Meta:
        verbose_name = "Message Recipient Group"
        verbose_name_plural = "Message Recipient Groups"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["message", "status"]),
            models.Index(fields=["status"]),
        ]
    def __str__(self):
        return f"{self.message.id} - {self.get_recipient_type_display()} - {self.get_status_display()}"
    @property
    def delivery_success_rate(self):
        if self.total_recipients == 0:
            return 0
        return round((self.delivered_count / self.total_recipients) * 100, 2)
