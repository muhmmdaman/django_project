from django.contrib import admin
from .models import Document
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "title",
        "document_type",
        "uploaded_by",
        "uploaded_at",
        "downloads",
    ]
    list_filter = ["document_type", "uploaded_at", "subject"]
    search_fields = ["subject__name", "title", "uploaded_by__username"]
    readonly_fields = ["uploaded_at", "downloads"]
    fieldsets = (
        ("Document Info", {"fields": ("subject", "title", "description")}),
        ("Details", {"fields": ("document_type", "file")}),
        ("Meta", {"fields": ("uploaded_by", "uploaded_at", "downloads")}),
    )
