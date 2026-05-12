"""Management command for database integrity checks and maintenance."""
from django.core.management.base import BaseCommand
from django.db.models import Count
from accounts.models import CustomUser
from students.models import Student, Marks, Subject, Teacher, Attendance
from analytics.models import Prediction
from messaging.models import Message, ActivityLog, UserRestriction
from complaints.models import Complaint
from documents.models import Document
class Command(BaseCommand):
    help = "Check database integrity and generate report"
    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Automatically fix identified issues",
        )
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("DATABASE INTEGRITY CHECK"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        issues_found = 0
        orphan_students = CustomUser.objects.filter(role="student").exclude(
            student_profile__isnull=False
        )
        if orphan_students.exists():
            issues_found += 1
            self.stdout.write(
                self.style.WARNING(
                    f"[!] {orphan_students.count()} student users without profiles"
                )
            )
        orphan_teachers = CustomUser.objects.filter(role="teacher").exclude(
            teacher_profile__isnull=False
        )
        if orphan_teachers.exists():
            issues_found += 1
            self.stdout.write(
                self.style.WARNING(
                    f"[!] {orphan_teachers.count()} teacher users without profiles"
                )
            )
        students_no_pred = (
            Student.objects.filter(marks__isnull=False)
            .exclude(prediction__isnull=False)
            .distinct()
        )
        if students_no_pred.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"[i] {students_no_pred.count()} students with marks but no predictions"
                )
            )
            if options["fix"]:
                count = 0
                for student in students_no_pred:
                    try:
                        Prediction.generate_prediction(student)
                        count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error for {student}: {e}"
                            )
                        )
                self.stdout.write(
                    self.style.SUCCESS(f"[OK] Generated {count} predictions")
                )
        duplicate_marks = (
            Marks.objects.values("student", "subject", "exam_type")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )
        if duplicate_marks.exists():
            issues_found += 1
            self.stdout.write(
                self.style.WARNING(
                    f"[!] {duplicate_marks.count()} duplicate mark entries"
                )
            )
        self.stdout.write("\n" + self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("DATABASE STATISTICS"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        stats = {
            "CustomUser": CustomUser.objects.count(),
            "Student": Student.objects.count(),
            "Teacher": Teacher.objects.count(),
            "Subject": Subject.objects.count(),
            "Marks": Marks.objects.count(),
            "Prediction": Prediction.objects.count(),
            "Message": Message.objects.count(),
            "ActivityLog": ActivityLog.objects.count(),
            "UserRestriction": UserRestriction.objects.count(),
            "Complaint": Complaint.objects.count(),
            "Document": Document.objects.count(),
            "Attendance": Attendance.objects.count(),
        }
        for model_name, count in stats.items():
            self.stdout.write(f"  {model_name}: {count}")
        self.stdout.write("\n" + self.style.SUCCESS("=" * 70))
        if issues_found == 0:
            self.stdout.write(
                self.style.SUCCESS("[OK] DATABASE INTEGRITY OK - No issues")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"[!] {issues_found} issue(s) found")
            )
        self.stdout.write(self.style.SUCCESS("=" * 70))
