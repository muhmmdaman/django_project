from django.db import models
from django.contrib.auth import get_user_model
from students.models import Subject
User = get_user_model()
class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
    ]
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="time_slots"
    )
    faculty = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "teacher"},
        related_name="teaching_slots",
    )
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=10)
    semester = models.IntegerField()
    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        unique_together = ["subject", "day_of_week", "start_time", "semester"]
    def __str__(self):
        return f"{self.subject} - {self.day_of_week} {self.start_time}"
