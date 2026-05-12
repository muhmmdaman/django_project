from django.db import models
from django.db.models import Avg, Count, F
class Prediction(models.Model):
    RISK_LEVELS = [
        ("low", "Low Risk"),
        ("medium", "Medium Risk"),
        ("high", "High Risk"),
        ("critical", "Critical Risk"),
    ]
    student = models.OneToOneField(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="prediction",
    )
    predicted_score = models.FloatField(
        help_text="Predicted average score (0-100)",
    )
    predicted_cgpa = models.FloatField(
        default=0.0,
        help_text="Predicted CGPA (0-10)",
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVELS,
        default="low",
    )
    attendance_risk = models.BooleanField(
        default=False,
        help_text="True if attendance is below 75%",
    )
    performance_trend = models.CharField(
        max_length=20,
        choices=[
            ("improving", "Improving"),
            ("stable", "Stable"),
            ("declining", "Declining"),
            ("new", "New Student"),
        ],
        default="new",
    )
    weak_subjects = models.JSONField(
        default=list,
        blank=True,
        help_text="List of weak subjects",
    )
    suggestions = models.TextField(
        blank=True,
        help_text="AI-generated suggestions for improvement",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
    def __str__(self):
        return f"{self.student} - Predicted: {self.predicted_score:.1f} ({self.get_risk_level_display()})"
    @classmethod
    def generate_prediction(cls, student):
        avg_marks = student.get_average_marks()
        attendance = student.attendance
        cgpa = student.calculate_cgpa()
        student.cgpa = cgpa
        student.save(update_fields=["cgpa"])
        attendance_risk = attendance < 75.0
        attendance_factor = attendance / 100.0
        marks_contribution = avg_marks * 0.6
        attendance_contribution = attendance_factor * 40
        predicted_score = marks_contribution + attendance_contribution
        if attendance_risk:
            predicted_score *= 0.9
        predicted_score = max(0, min(100, predicted_score))
        predicted_cgpa = student.score_to_grade_point(predicted_score)
        performance_trend = cls._analyze_trend(student)
        weak_subjects = [
            {"code": sub.code, "name": sub.name, "score": score}
            for sub, score in student.get_weakest_subjects()
        ]
        risk_level = cls._calculate_risk_level(
            avg_marks, attendance, predicted_score, performance_trend
        )
        suggestions = cls._generate_suggestions(
            student, avg_marks, attendance, risk_level, weak_subjects
        )
        prediction, _ = cls.objects.update_or_create(
            student=student,
            defaults={
                "predicted_score": round(predicted_score, 2),
                "predicted_cgpa": round(predicted_cgpa, 2),
                "risk_level": risk_level,
                "attendance_risk": attendance_risk,
                "performance_trend": performance_trend,
                "weak_subjects": weak_subjects,
                "suggestions": suggestions,
            },
        )
        return prediction
    @staticmethod
    def _analyze_trend(student):
        history = student.performance_history.order_by("semester")
        if history.count() < 2:
            return "new"
        recent = list(history.values_list("sgpa", flat=True))[-3:]
        if len(recent) < 2:
            return "new"
        if recent[-1] > recent[-2] + 0.3:
            return "improving"
        elif recent[-1] < recent[-2] - 0.3:
            return "declining"
        return "stable"
    @staticmethod
    def _calculate_risk_level(avg_marks, attendance, predicted_score, trend):
        if (
            predicted_score < 35
            or avg_marks < 30
            or attendance < 50
            or (avg_marks < 45 and attendance < 60)
        ):
            return "critical"
        if predicted_score < 50 or avg_marks < 40 or attendance < 60:
            return "high"
        if trend == "declining" and (predicted_score < 60 or attendance < 70):
            return "high"
        if predicted_score < 70 or avg_marks < 60 or attendance < 75:
            return "medium"
        return "low"
    @staticmethod
    def _generate_suggestions(
        student, avg_marks, attendance, risk_level, weak_subjects
    ):
        suggestions = []
        if weak_subjects:
            for ws in weak_subjects[:2]:
                suggestions.append(
                    f"Focus on {ws['name']} ({ws['code']}) - current score: {ws['score']:.0f}%"
                )
        if attendance < 50:
            suggestions.append(
                "CRITICAL: Attendance is severely low. You may face debarment from exams."
            )
        elif attendance < 60:
            suggestions.append(
                "URGENT: Improve attendance immediately. Minimum 60% required for exams."
            )
        elif attendance < 75:
            suggestions.append(
                "Warning: Attendance below 75%. Maintain consistency to avoid penalties."
            )
        elif attendance >= 90:
            suggestions.append("Excellent attendance! Keep maintaining it.")
        if avg_marks < 35:
            suggestions.append(
                "CRITICAL: Seek immediate academic counseling. Consider remedial classes."
            )
        elif avg_marks < 45:
            suggestions.append("URGENT: Join study groups and attend extra tutorials.")
        elif avg_marks < 55:
            suggestions.append(
                "Practice previous year papers. Focus on scoring subjects first."
            )
        elif avg_marks < 70:
            suggestions.append(
                "Good progress! Target 70+ in all subjects for better CGPA."
            )
        elif avg_marks >= 85:
            suggestions.append(
                "Outstanding! Aim for university rank. Consider research opportunities."
            )
        cgpa = student.cgpa or 0
        if cgpa < 5.0 and cgpa > 0:
            suggestions.append(
                "CGPA is below passing threshold. Prioritize clearing backlogs."
            )
        elif 5.0 <= cgpa < 7.0:
            suggestions.append(
                "Target CGPA improvement. Consistent 70+ scores will help."
            )
        elif cgpa >= 8.5:
            suggestions.append(
                "Excellent CGPA! You're eligible for higher studies and placements."
            )
        if risk_level == "critical":
            suggestions.append(
                "ACTION REQUIRED: Meet HOD/Dean immediately. Academic probation possible."
            )
        elif risk_level == "high":
            suggestions.append(
                "Schedule meeting with faculty advisor within this week."
            )
        return "\n".join(suggestions)
    def get_risk_color(self):
        colors = {
            "low": "success",
            "medium": "warning",
            "high": "danger",
            "critical": "dark",
        }
        return colors.get(self.risk_level, "secondary")
    def get_risk_icon(self):
        icons = {
            "low": "check-circle-fill",
            "medium": "exclamation-triangle-fill",
            "high": "x-circle-fill",
            "critical": "exclamation-octagon-fill",
        }
        return icons.get(self.risk_level, "question-circle")
    def get_trend_icon(self):
        icons = {
            "improving": "arrow-up-circle-fill",
            "stable": "dash-circle-fill",
            "declining": "arrow-down-circle-fill",
            "new": "star-fill",
        }
        return icons.get(self.performance_trend, "circle")
    def get_trend_color(self):
        colors = {
            "improving": "success",
            "stable": "info",
            "declining": "danger",
            "new": "primary",
        }
        return colors.get(self.performance_trend, "secondary")
class PerformanceAnalytics:
    @staticmethod
    def get_top_performers(department=None, semester=None, limit=10):
        from students.models import Student
        qs = Student.objects.filter(cgpa__isnull=False, cgpa__gt=0)
        if department:
            qs = qs.filter(department=department)
        if semester:
            qs = qs.filter(semester=semester)
        return qs.order_by("-cgpa")[:limit]
    @staticmethod
    def get_most_improved(limit=5):
        from students.models import Student, PerformanceHistory
        improved = []
        for student in Student.objects.prefetch_related("performance_history"):
            history = list(student.performance_history.order_by("-semester")[:2])
            if len(history) >= 2:
                improvement = history[0].sgpa - history[1].sgpa
                if improvement > 0:
                    improved.append((student, improvement))
        improved.sort(key=lambda x: x[1], reverse=True)
        return improved[:limit]
    @staticmethod
    def get_consistently_low_performers(limit=10):
        return Prediction.objects.filter(
            risk_level__in=["high", "critical"]
        ).select_related("student")[:limit]
    @staticmethod
    def get_department_stats():
        from students.models import Student
        stats = (
            Student.objects.values("department")
            .annotate(
                total=Count("id"),
                avg_cgpa=Avg("cgpa"),
                avg_attendance=Avg("attendance"),
            )
            .order_by("department")
        )
        return list(stats)
    @staticmethod
    def get_risk_distribution():
        return (
            Prediction.objects.values("risk_level")
            .annotate(count=Count("id"))
            .order_by("risk_level")
        )
    @staticmethod
    def get_alerts(student=None):
        alerts = []
        if student:
            if student.attendance < 60:
                alerts.append(
                    {
                        "type": "danger",
                        "icon": "exclamation-octagon-fill",
                        "message": f"Critical: Attendance is only {student.attendance:.0f}%",
                    }
                )
            elif student.attendance < 75:
                alerts.append(
                    {
                        "type": "warning",
                        "icon": "exclamation-triangle-fill",
                        "message": f"Warning: Attendance ({student.attendance:.0f}%) below 75%",
                    }
                )
            cgpa = student.cgpa or 0
            if cgpa < 4.0 and cgpa > 0:
                alerts.append(
                    {
                        "type": "danger",
                        "icon": "x-circle-fill",
                        "message": f"Critical: CGPA ({cgpa:.2f}) below passing threshold",
                    }
                )
            elif cgpa < 5.5 and cgpa > 0:
                alerts.append(
                    {
                        "type": "warning",
                        "icon": "exclamation-triangle-fill",
                        "message": f"Warning: CGPA ({cgpa:.2f}) needs improvement",
                    }
                )
            try:
                if student.prediction.performance_trend == "declining":
                    alerts.append(
                        {
                            "type": "warning",
                            "icon": "arrow-down-circle-fill",
                            "message": "Performance trend is declining",
                        }
                    )
            except Prediction.DoesNotExist:
                pass
        return alerts
