from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Administrator"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    is_restricted = models.BooleanField(
        default=False,
        help_text="Quick lookup cache for whether user has active restrictions",
    )
    last_activity = models.DateTimeField(
        null=True, blank=True, help_text="Track last active timestamp"
    )
    messaging_enabled = models.BooleanField(
        default=True, help_text="Admin toggle for messaging features"
    )
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    @property
    def is_student(self):
        return self.role == "student"
    @property
    def is_teacher(self):
        return self.role == "teacher"
    @property
    def is_admin(self):
        return self.role == "admin"
    def set_restricted_status(self):
        from messaging.models import UserRestriction
        has_active_restrictions = UserRestriction.objects.filter(
            user=self, is_active=True
        ).exists()
        if self.is_restricted != has_active_restrictions:
            self.is_restricted = has_active_restrictions
            self.save(update_fields=["is_restricted"])
        return self.is_restricted
