from django.contrib import admin
from .models import TimeSlot
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "day_of_week",
        "start_time",
        "end_time",
        "faculty",
        "room_number",
    ]
    list_filter = ["day_of_week", "department", "semester"]
    search_fields = ["subject__name", "faculty__username", "room_number"]
    fieldsets = (
        ("Subject & Faculty", {"fields": ("subject", "faculty")}),
        ("Schedule", {"fields": ("day_of_week", "start_time", "end_time")}),
        ("Location & Details", {"fields": ("room_number", "department", "semester")}),
    )
