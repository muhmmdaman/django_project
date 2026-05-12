"""Management command to assign subjects to teachers (7-8 subjects per teacher).
Each teacher gets subjects relevant to their department.
"""
from django.core.management.base import BaseCommand
from students.models import Subject, Teacher
import random
class Command(BaseCommand):
    help = "Assign 7-8 subjects to each teacher in their department"
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing subject assignments before assigning new ones",
        )
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing subject assignments...")
            for teacher in Teacher.objects.all():
                teacher.subjects.clear()
            self.stdout.write(self.style.SUCCESS("[OK] All assignments cleared"))
        try:
            self.assign_subjects_to_teachers()
            self.stdout.write(
                self.style.SUCCESS("[OK] Subjects assigned successfully!")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] {str(e)}"))
            import traceback
            traceback.print_exc()
    def assign_subjects_to_teachers(self):
        teachers = Teacher.objects.all()
        total_assignments = 0
        for teacher in teachers:
            dept_subjects = Subject.objects.filter(
                department=teacher.department
            ).order_by("?")
            if not dept_subjects.exists():
                dept_subjects = Subject.objects.filter(department="GEN").order_by("?")
            num_subjects = random.randint(7, 8)
            subjects_to_assign = dept_subjects[:num_subjects]
            if subjects_to_assign:
                teacher.subjects.set(subjects_to_assign)
                total_assignments += len(subjects_to_assign)
                subject_list = ", ".join([f"{s.code}" for s in subjects_to_assign[:3]])
                extra = (
                    f" +{len(subjects_to_assign) - 3} more"
                    if len(subjects_to_assign) > 3
                    else ""
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   [OK] {teacher.user.get_full_name()} ({teacher.department}): {subject_list}{extra}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"   [SKIP] {teacher.user.get_full_name()}: No subjects available"
                    )
                )
        self.stdout.write(f"\n[STATS] Total subject assignments: {total_assignments}")
        self.stdout.write(f"[STATS] Total teachers: {teachers.count()}")
