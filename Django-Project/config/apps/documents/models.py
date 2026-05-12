from django.db import models
from django.contrib.auth import get_user_model
from students.models import Subject
User = get_user_model()
class Document(models.Model):
    DOCUMENT_TYPES = [
        ("notes", "Class Notes"),
        ("assignment", "Assignment"),
        ("solution", "Solution"),
        ("reference", "Reference Material"),
    ]
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="documents"
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_documents"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, default="notes"
    )
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    downloads = models.IntegerField(default=0)
    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
    def __str__(self):
        return f"{self.subject} - {self.title}"
    def increment_downloads(self):
        self.downloads += 1
        self.save(update_fields=["downloads"])
