from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import Student, Subject
from timetable.models import TimeSlot
from documents.models import Document
from messaging.models import Message
from complaints.models import Complaint
import random
User = get_user_model()
class Command(BaseCommand):
    help = "Generate sample data for messaging, timetable, and documents"
    def handle(self, *args, **options):
        self.stdout.write("Generating sample data...")
        students = Student.objects.all()
        teachers = User.objects.filter(role="teacher")
        subjects = Subject.objects.all()
        if not teachers.exists():
            teacher = User.objects.create_user(
                username="teacher1",
                email="teacher1@university.edu",
                first_name="John",
                last_name="Professor",
                password="teacher123",
                role="teacher",
            )
            teachers = User.objects.filter(role="teacher")
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for subject in subjects[:10]:
            for day_idx, day in enumerate(days[:3]):
                start_hour = 9 + (day_idx % 3)
                TimeSlot.objects.get_or_create(
                    subject=subject,
                    day_of_week=day,
                    defaults={
                        "faculty": random.choice(teachers),
                        "start_time": f"{start_hour:02d}:00",
                        "end_time": f"{start_hour+1:02d}:00",
                        "room_number": f"Room {random.randint(101, 301)}",
                        "department": subject.department,
                        "semester": subject.semester,
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"Created timetable slots"))
        for subject in subjects[:15]:
            for doc_type in ["notes", "assignment", "solution", "reference"]:
                Document.objects.get_or_create(
                    subject=subject,
                    title=f"{subject.name} - {doc_type.title()}",
                    defaults={
                        "uploaded_by": random.choice(teachers),
                        "description": f"This is a sample {doc_type} for {subject.name}",
                        "document_type": doc_type,
                        "file": "documents/sample.pdf",
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"Created sample documents"))
        student_users = [s.user for s in students[:5]]
        teacher_list = list(teachers[:3])
        for i, sender in enumerate(student_users[:3]):
            receiver = student_users[(i + 1) % len(student_users)]
            Message.objects.get_or_create(
                sender=sender,
                receiver=receiver,
                message_type="private",
                defaults={
                    "content": f"Hi {receiver.get_full_name()}, how are you doing with the assignments?",
                },
            )
        for teacher in teacher_list[:2]:
            for student in student_users[:3]:
                Message.objects.get_or_create(
                    sender=teacher,
                    receiver=student,
                    message_type="private",
                    defaults={
                        "content": f"Hi {student.get_full_name()}, good work on the last assignment!",
                    },
                )
        departments = ["CSE", "IT", "ECE", "GEN"]
        Message.objects.get_or_create(
            sender=teacher_list[0],
            message_type="broadcast",
            department=None,
            defaults={
                "content": "Important: All classes will be held as per the scheduled timetable. No changes this week.",
            },
        )
        for dept in departments:
            Message.objects.get_or_create(
                sender=random.choice(teacher_list),
                message_type="broadcast",
                department=dept,
                defaults={
                    "content": f"{dept} Department: Midterm exam schedule will be announced soon.",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created sample messages"))
        for student in students[:5]:
            Complaint.objects.get_or_create(
                student=student,
                title=f"Sample complaint from {student.user.first_name}",
                defaults={
                    "description": "This is a sample complaint for testing purposes.",
                    "complaint_type": random.choice(
                        ["infrastructure", "academic", "other"]
                    ),
                    "status": random.choice(["pending", "in_progress", "resolved"]),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created sample complaints"))
        self.stdout.write(self.style.SUCCESS("Sample data generated successfully!"))
