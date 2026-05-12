from django.contrib import admin
from django.utils.html import format_html
from .models import Prediction
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "predicted_score_display",
        "risk_level_display",
        "attendance_risk_display",
        "updated_at",
    ]
    list_filter = ["risk_level", "attendance_risk", "updated_at"]
    search_fields = [
        "student__user__username",
        "student__user__first_name",
        "student__user__last_name",
    ]
    ordering = ["-updated_at"]
    readonly_fields = [
        "student",
        "predicted_score",
        "risk_level",
        "attendance_risk",
        "suggestions",
        "created_at",
        "updated_at",
    ]
    list_per_page = 20
    fieldsets = (
        (
            "Student",
            {"fields": ("student",)},
        ),
        (
            "Prediction Results",
            {"fields": ("predicted_score", "risk_level", "attendance_risk")},
        ),
        (
            "Recommendations",
            {"fields": ("suggestions",), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    @admin.display(description="Predicted Score")
    def predicted_score_display(self, obj):
        color = "#2ecc71"
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{:.1f}%</span>',
            color,
            obj.predicted_score,
        )
    @admin.display(description="Risk Level")
    def risk_level_display(self, obj):
        colors = {"low": "#2ecc71", "medium": "#f39c12", "high": "#e74c3c", "critical": "#c0392b"}
        color = colors.get(obj.risk_level, "#7f8c8d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display(),
        )
    @admin.display(description="Attendance Risk")
    def attendance_risk_display(self, obj):
        if obj.attendance_risk:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold; padding: 4px 8px; background-color: #fadbd8; border-radius: 3px;">⚠ At Risk</span>'
            )
        return format_html(
            '<span style="color: #2ecc71; font-weight: bold; padding: 4px 8px; background-color: #d5f4e6; border-radius: 3px;">✓ Good</span>'
        )
