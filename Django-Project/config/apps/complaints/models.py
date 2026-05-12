from django.db import models
from students.models import Student
class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ("infrastructure", "Infrastructure"),
        ("academic", "Academic"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="complaints"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    complaint_type = models.CharField(
        max_length=20, choices=COMPLAINT_TYPES, default="other"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_notes = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"
    def __str__(self):
        return f"{self.student} - {self.title} ({self.status})"
