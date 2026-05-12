"""Management command to populate the database with sample data for demonstration.
Adds messages, restrictions, restrictions, and activity logs.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from accounts.models import CustomUser
from students.models import Student, Teacher, Marks
from messaging.models import Message, ActivityLog, UserRestriction
class Command(BaseCommand):
    help = "Populate database with sample messages, restrictions, and activity logs"
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing messages and restrictions before populating",
        )
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Message.objects.all().delete()
            UserRestriction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))
        self.stdout.write("Starting data population...")
        teachers = CustomUser.objects.filter(role="teacher")
        students = CustomUser.objects.filter(role="student")
        admins = CustomUser.objects.filter(role="admin")
        if not teachers or not students:
            self.stdout.write(
                self.style.ERROR(
                    "Not enough teachers or students. Run setup_university_data first."
                )
            )
            return
        self.stdout.write("Creating sample messages...")
        message_count = 0
        for _ in range(15):
            sender = random.choice(students)
            receiver = random.choice(students)
            if sender != receiver:
                Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    message_type="private",
                    content=f"Hi! How are you doing? Let's study together for the upcoming exam.",
                    receiver_type="individual",
                    created_via="ui",
                )
                message_count += 1
        for _ in range(10):
            sender = random.choice(students)
            receiver = random.choice(teachers)
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                message_type="private",
                content=f"Sir/Madam, I have a doubt in the last lecture. Can you explain it again?",
                receiver_type="individual",
                created_via="ui",
            )
            message_count += 1
        for _ in range(10):
            sender = random.choice(teachers)
            receiver = random.choice(students)
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                message_type="private",
                content=f"Please submit your assignment by Friday.",
                receiver_type="individual",
                created_via="ui",
            )
            message_count += 1
        departments = ["CSE", "IT", "ECE", "GEN"]
        for _ in range(12):
            sender = random.choice(teachers)
            dept = random.choice(departments)
            Message.objects.create(
                sender=sender,
                message_type="broadcast",
                department=dept,
                content=f"Important announcement: Department {dept} meeting scheduled for next week. Please mark your calendar.",
                receiver_type="department",
                created_via="ui",
            )
            message_count += 1
        for _ in range(8):
            sender = random.choice(admins)
            Message.objects.create(
                sender=sender,
                message_type="broadcast",
                content=f"System maintenance scheduled for this weekend. Please plan accordingly.",
                receiver_type="all_users",
                created_via="ui",
            )
            message_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"[OK] Created {message_count} sample messages")
        )
        self.stdout.write("Creating sample restrictions...")
        restriction_count = 0
        to_ban = random.sample(list(students), min(3, len(students)))
        for student in to_ban:
            ban_admin = random.choice(admins)
            UserRestriction.objects.filter(
                user=student, restriction_type="banned"
            ).delete()
            restriction = UserRestriction.objects.create(
                user=student,
                restriction_type="banned",
                reason="Violating community guidelines",
                is_active=True,
                restricted_by=ban_admin,
                expires_at=timezone.now() + timedelta(days=7),
            )
            restriction_count += 1
            self.stdout.write(f"  - Banned {student.username} (expires in 7 days)")
        to_mute = random.sample(list(students), min(4, len(students)))
        for student in to_mute:
            if student not in to_ban:
                mute_admin = random.choice(admins)
                UserRestriction.objects.filter(
                    user=student, restriction_type="muted"
                ).delete()
                restriction = UserRestriction.objects.create(
                    user=student,
                    restriction_type="muted",
                    reason="Excessive messaging",
                    is_active=True,
                    restricted_by=mute_admin,
                    expires_at=timezone.now() + timedelta(days=3),
                )
                restriction_count += 1
                self.stdout.write(f"  - Muted {student.username} (expires in 3 days)")
        self.stdout.write(
            self.style.SUCCESS(f"[OK] Created {restriction_count} sample restrictions")
        )
        self.stdout.write("Creating sample activity logs...")
        activity_count = 0
        for _ in range(20):
            user = random.choice(list(teachers) + list(students) + list(admins))
            ActivityLog.objects.create(
                user=user,
                action_type="login",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
            )
            activity_count += 1
        for _ in range(15):
            user = random.choice(list(teachers) + list(students))
            ActivityLog.objects.create(
                user=user,
                action_type="message_sent",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
            )
            activity_count += 1
        for _ in range(10):
            user = random.choice(list(teachers) + list(admins))
            ActivityLog.objects.create(
                user=user,
                action_type="broadcast_sent",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
            )
            activity_count += 1
        for _ in range(5):
            admin = random.choice(admins)
            student = random.choice(students)
            action_type = random.choice(["user_banned", "user_muted"])
            ActivityLog.objects.create(
                user=admin,
                action_type=action_type,
                target_user=student,
                ip_address=f"192.168.1.{random.randint(1, 255)}",
            )
            activity_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"[OK] Created {activity_count} sample activity logs")
        )
        self.stdout.write("Creating sample salary payments...")
        salary_count = 0
        try:
            from students.models import SalaryPayment, Teacher
            teacher_profiles = Teacher.objects.all()[:8]
            for teacher in teacher_profiles:
                for months_ago in [0, 1, 2]:
                    payment_date = (
                        timezone.now() - timedelta(days=30 * months_ago)
                    ).date()
                    admin = random.choice(admins)
                    payment = SalaryPayment.objects.create(
                        teacher=teacher,
                        amount=50000 + random.randint(0, 20000),
                        payment_date=payment_date,
                        payment_method=random.choice(
                            ["bank_transfer", "check", "cash", "other"]
                        ),
                        reference_number=f"SALARY-{teacher.id}-{payment_date.strftime('%Y%m%d')}",
                        processed_by=admin,
                        notes=f"Monthly salary for {payment_date.strftime('%B %Y')}",
                    )
                    salary_count += 1
                    if months_ago == 0:
                        teacher.salary_status = "paid"
                        teacher.last_paid_date = payment_date
                        teacher.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] Created {salary_count} sample salary payments"
                )
            )
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    "SalaryPayment model not found, skipping salary data"
                )
            )
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("[OK] Data population complete!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"  - Messages created: {message_count}")
        self.stdout.write(f"  - Restrictions created: {restriction_count}")
        self.stdout.write(f"  - Activity logs created: {activity_count}")
        self.stdout.write(f"  - Salary payments created: {salary_count}")
        self.stdout.write(f"\nAll sections should now display data properly.")
        self.stdout.write(
            f"Total database records: {Message.objects.count()} messages, "
            f"{UserRestriction.objects.count()} restrictions, "
            f"{ActivityLog.objects.count()} activity logs"
        )
