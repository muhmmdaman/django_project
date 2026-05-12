from django.contrib import admin
from .models import Complaint
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ["student", "title", "complaint_type", "status", "created_at"]
    list_filter = ["complaint_type", "status", "created_at"]
    search_fields = ["student__user__username", "title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Student Info", {"fields": ("student",)}),
        ("Complaint", {"fields": ("title", "description", "complaint_type")}),
        ("Status", {"fields": ("status", "resolution_notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
