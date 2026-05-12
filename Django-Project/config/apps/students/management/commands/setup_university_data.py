import random
from datetime import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from accounts.models import CustomUser
from students.models import (
    Student,
    Subject,
    Marks,
    PerformanceHistory,
    Teacher,
    Attendance,
)
from analytics.models import Prediction
from timetable.models import TimeSlot
class Command(BaseCommand):
    help = "Create realistic sample university data with Indian names"
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before creating new",
        )
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            TimeSlot.objects.all().delete()
            Attendance.objects.all().delete()
            Marks.objects.all().delete()
            PerformanceHistory.objects.all().delete()
            Prediction.objects.all().delete()
            Student.objects.all().delete()
            Teacher.objects.all().delete()
            Subject.objects.all().delete()
            CustomUser.objects.filter(role__in=["student", "teacher"]).delete()
        self.stdout.write("Creating university sample data...")
        with transaction.atomic():
            self.create_subjects()
            self.create_teachers()
            self.create_students()
            self.create_marks()
            self.create_performance_history()
            self.create_attendance_records()
            self.generate_predictions()
            self.create_timetable()
        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))
        self.print_login_credentials()
    def create_subjects(self):
        subjects_data = [
            ("CS101", "Programming Fundamentals", "CSE", 1, 4, False),
            ("CS102", "Digital Logic Design", "CSE", 1, 3, False),
            ("CS103", "Computer Organization", "CSE", 1, 3, False),
            ("MA101", "Engineering Mathematics I", "CSE", 1, 4, False),
            ("PH101", "Engineering Physics", "CSE", 1, 3, False),
            ("EN101", "Technical Communication", "CSE", 1, 2, False),
            ("CS111", "Programming Lab", "CSE", 1, 2, True),
            ("CS112", "Digital Logic Lab", "CSE", 1, 2, True),
            ("PH111", "Physics Lab", "CSE", 1, 1, True),
            ("EN111", "Language Lab", "CSE", 1, 1, True),
            ("CS201", "Data Structures", "CSE", 2, 4, False),
            ("CS202", "Object Oriented Programming", "CSE", 2, 4, False),
            ("CS203", "Discrete Mathematics", "CSE", 2, 3, False),
            ("MA201", "Engineering Mathematics II", "CSE", 2, 4, False),
            ("CH201", "Engineering Chemistry", "CSE", 2, 3, False),
            ("HS201", "Professional Ethics", "CSE", 2, 2, False),
            ("CS211", "Data Structures Lab", "CSE", 2, 2, True),
            ("CS212", "OOP Lab", "CSE", 2, 2, True),
            ("CH211", "Chemistry Lab", "CSE", 2, 1, True),
            ("HS211", "Presentation Skills Lab", "CSE", 2, 1, True),
            ("CS301", "Database Management Systems", "CSE", 3, 4, False),
            ("CS302", "Operating Systems", "CSE", 3, 4, False),
            ("CS303", "Computer Networks", "CSE", 3, 3, False),
            ("CS304", "Theory of Computation", "CSE", 3, 3, False),
            ("MA301", "Probability and Statistics", "CSE", 3, 3, False),
            ("EC301", "Microprocessors", "CSE", 3, 3, False),
            ("CS311", "DBMS Lab", "CSE", 3, 2, True),
            ("CS312", "OS Lab", "CSE", 3, 2, True),
            ("CS313", "Networks Lab", "CSE", 3, 1, True),
            ("EC311", "Microprocessors Lab", "CSE", 3, 2, True),
            ("CS501", "Machine Learning", "CSE", 5, 4, False),
            ("CS502", "Web Technologies", "CSE", 5, 3, False),
            ("CS503", "Compiler Design", "CSE", 5, 4, False),
            ("CS504", "Software Engineering", "CSE", 5, 3, False),
            ("CS505", "Cloud Computing", "CSE", 5, 3, False),
            ("CS506", "Cryptography", "CSE", 5, 3, False),
            ("CS511", "ML Lab", "CSE", 5, 2, True),
            ("CS512", "Web Tech Lab", "CSE", 5, 2, True),
            ("CS513", "Compiler Lab", "CSE", 5, 1, True),
            ("CS514", "Software Project Lab", "CSE", 5, 2, True),
            ("CS701", "Artificial Intelligence", "CSE", 7, 4, False),
            ("CS702", "Big Data Analytics", "CSE", 7, 3, False),
            ("CS703", "Internet of Things", "CSE", 7, 3, False),
            ("CS704", "Blockchain Technology", "CSE", 7, 3, False),
            ("CS705", "Mobile Computing", "CSE", 7, 3, False),
            ("CS706", "Information Security", "CSE", 7, 3, False),
            ("CS711", "AI Lab", "CSE", 7, 2, True),
            ("CS712", "Big Data Lab", "CSE", 7, 2, True),
            ("CS713", "IoT Lab", "CSE", 7, 1, True),
            ("CS714", "Blockchain Lab", "CSE", 7, 2, True),
            ("IT301", "Database Systems", "IT", 3, 4, False),
            ("IT302", "Web Programming", "IT", 3, 4, False),
            ("IT303", "Computer Networks", "IT", 3, 3, False),
            ("IT304", "Software Engineering", "IT", 3, 3, False),
            ("IT305", "Operating Systems", "IT", 3, 3, False),
            ("MA302", "Discrete Mathematics", "IT", 3, 3, False),
            ("IT311", "Database Lab", "IT", 3, 2, True),
            ("IT312", "Web Programming Lab", "IT", 3, 2, True),
            ("IT313", "Networks Lab", "IT", 3, 1, True),
            ("IT314", "OS Lab", "IT", 3, 2, True),
            ("IT501", "Data Analytics", "IT", 5, 4, False),
            ("IT502", "Cloud Computing", "IT", 5, 3, False),
            ("IT503", "Mobile Application Dev", "IT", 5, 4, False),
            ("IT504", "Network Security", "IT", 5, 3, False),
            ("IT505", "Data Science", "IT", 5, 3, False),
            ("IT506", "DevOps", "IT", 5, 3, False),
            ("IT511", "Data Analytics Lab", "IT", 5, 2, True),
            ("IT512", "Cloud Lab", "IT", 5, 2, True),
            ("IT513", "Mobile Dev Lab", "IT", 5, 1, True),
            ("IT514", "Security Lab", "IT", 5, 2, True),
            ("IT701", "Advanced Databases", "IT", 7, 4, False),
            ("IT702", "Information Retrieval", "IT", 7, 3, False),
            ("IT703", "Cyber Security", "IT", 7, 3, False),
            ("IT704", "Human Computer Interaction", "IT", 7, 3, False),
            ("IT705", "Distributed Systems", "IT", 7, 3, False),
            ("IT706", "Business Intelligence", "IT", 7, 3, False),
            ("IT711", "Advanced DB Lab", "IT", 7, 2, True),
            ("IT712", "IR Lab", "IT", 7, 2, True),
            ("IT713", "Security Lab", "IT", 7, 1, True),
            ("IT714", "BI Lab", "IT", 7, 2, True),
            ("EC301E", "Digital Signal Processing", "ECE", 3, 4, False),
            ("EC302", "Electromagnetic Fields", "ECE", 3, 4, False),
            ("EC303", "Analog Communication", "ECE", 3, 3, False),
            ("EC304", "Control Systems", "ECE", 3, 3, False),
            ("EC305", "Electronic Circuits", "ECE", 3, 3, False),
            ("MA303", "Transforms and PDEs", "ECE", 3, 3, False),
            ("EC311E", "DSP Lab", "ECE", 3, 2, True),
            ("EC312", "Communication Lab", "ECE", 3, 2, True),
            ("EC313", "Control Lab", "ECE", 3, 1, True),
            ("EC314", "Circuits Lab", "ECE", 3, 2, True),
            ("EC501", "Digital Communication", "ECE", 5, 4, False),
            ("EC502", "VLSI Design", "ECE", 5, 4, False),
            ("EC503", "Embedded Systems", "ECE", 5, 3, False),
            ("EC504", "Microwave Engineering", "ECE", 5, 3, False),
            ("EC505", "Optical Communication", "ECE", 5, 3, False),
            ("EC506", "Signal Processing", "ECE", 5, 3, False),
            ("EC511", "Digital Comm Lab", "ECE", 5, 2, True),
            ("EC512", "VLSI Lab", "ECE", 5, 2, True),
            ("EC513", "Embedded Lab", "ECE", 5, 1, True),
            ("EC514", "Microwave Lab", "ECE", 5, 2, True),
            ("EC701", "Wireless Communication", "ECE", 7, 4, False),
            ("EC702", "Antenna Theory", "ECE", 7, 3, False),
            ("EC703", "MEMS", "ECE", 7, 3, False),
            ("EC704", "Satellite Communication", "ECE", 7, 3, False),
            ("EC705", "RF Circuit Design", "ECE", 7, 3, False),
            ("EC706", "Biomedical Instrumentation", "ECE", 7, 3, False),
            ("EC711", "Wireless Lab", "ECE", 7, 2, True),
            ("EC712", "Antenna Lab", "ECE", 7, 2, True),
            ("EC713", "RF Lab", "ECE", 7, 1, True),
            ("EC714", "Biomedical Lab", "ECE", 7, 2, True),
            ("GEN101", "Environmental Science", "GEN", 1, 2, False),
            ("GEN201", "Constitution of India", "GEN", 2, 2, False),
            ("GEN301", "Professional Ethics", "GEN", 3, 2, False),
        ]
        for code, name, dept, sem, credits, is_lab in subjects_data:
            Subject.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": dept,
                    "semester": sem,
                    "credits": credits,
                    "is_lab": is_lab,
                },
            )
        self.stdout.write(f"  Created {len(subjects_data)} subjects")
    def create_teachers(self):
        teachers_data = [
            ("Dr. Rajesh", "Kumar", "CSE", "Professor", "TECH001", "+91-9876543210"),
            (
                "Prof. Anil",
                "Sharma",
                "CSE",
                "Associate Professor",
                "TECH002",
                "+91-9876543211",
            ),
            (
                "Dr. Kavita",
                "Desai",
                "CSE",
                "Assistant Professor",
                "TECH007",
                "+91-9876543216",
            ),
            (
                "Dr. Anita",
                "Singh",
                "CSE",
                "Associate Professor",
                "TECH009",
                "+91-9876543218",
            ),
            (
                "Prof. Sanjay",
                "Verma",
                "CSE",
                "Assistant Professor",
                "TECH011",
                "+91-9876543220",
            ),
            ("Dr. Meenakshi", "Rajan", "CSE", "Professor", "TECH012", "+91-9876543221"),
            ("Dr. Priya", "Menon", "IT", "Professor", "TECH003", "+91-9876543212"),
            (
                "Prof. Vivek",
                "Gupta",
                "IT",
                "Assistant Professor",
                "TECH004",
                "+91-9876543213",
            ),
            (
                "Prof. Suresh",
                "Nair",
                "IT",
                "Assistant Professor",
                "TECH008",
                "+91-9876543217",
            ),
            (
                "Dr. Lakshmi",
                "Pillai",
                "IT",
                "Associate Professor",
                "TECH013",
                "+91-9876543222",
            ),
            (
                "Dr. Sneha",
                "Iyer",
                "ECE",
                "Associate Professor",
                "TECH005",
                "+91-9876543214",
            ),
            (
                "Prof. Ramesh",
                "Yadav",
                "ECE",
                "Assistant Professor",
                "TECH006",
                "+91-9876543215",
            ),
            (
                "Prof. Vikram",
                "Malhotra",
                "ECE",
                "Professor",
                "TECH010",
                "+91-9876543219",
            ),
            (
                "Dr. Sunita",
                "Agarwal",
                "ECE",
                "Assistant Professor",
                "TECH014",
                "+91-9876543223",
            ),
        ]
        for first, last, dept, designation, emp_id, phone in teachers_data:
            username = f"{first.lower().replace('dr. ', '').replace('prof. ', '')}.{last.lower()}"
            email = f"{emp_id.lower()}@university.edu"
            if CustomUser.objects.filter(username=username).exists():
                continue
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                password="prof123",
                role="teacher",
            )
            teacher = Teacher.objects.create(
                user=user,
                employee_id=emp_id,
                department=dept,
                designation=designation,
                phone=phone,
            )
            subjects = Subject.objects.filter(department=dept)[:4]
            teacher.subjects.set(subjects)
        self.stdout.write(f"  Created {len(teachers_data)} teachers")
    def create_students(self):
        students_data = [
            ("Aarav", "Mehta", "CSE", 1, 85.5, "2025CSE001"),
            ("Diya", "Sharma", "CSE", 1, 90.0, "2025CSE002"),
            ("Vihaan", "Patel", "CSE", 1, 78.5, "2025CSE003"),
            ("Ananya", "Reddy", "CSE", 1, 72.0, "2025CSE004"),
            ("Reyansh", "Singh", "CSE", 1, 65.0, "2025CSE005"),
            ("Kiara", "Gupta", "CSE", 1, 88.0, "2025CSE006"),
            ("Advait", "Kumar", "CSE", 1, 55.0, "2025CSE007"),
            ("Saanvi", "Verma", "CSE", 1, 92.5, "2025CSE008"),
            ("Rahul", "Sharma", "CSE", 3, 88.5, "2024CSE001"),
            ("Priya", "Patel", "CSE", 3, 92.0, "2024CSE002"),
            ("Amit", "Kumar", "CSE", 3, 72.5, "2024CSE003"),
            ("Sneha", "Reddy", "CSE", 3, 65.0, "2024CSE004"),
            ("Vikram", "Singh", "CSE", 3, 45.0, "2024CSE005"),
            ("Neha", "Joshi", "CSE", 3, 80.0, "2024CSE006"),
            ("Aditya", "Nair", "CSE", 3, 75.5, "2024CSE007"),
            ("Pooja", "Iyer", "CSE", 3, 85.0, "2024CSE008"),
            ("Anjali", "Verma", "CSE", 5, 85.0, "2023CSE001"),
            ("Rohan", "Gupta", "CSE", 5, 78.5, "2023CSE002"),
            ("Kavya", "Nair", "CSE", 5, 55.0, "2023CSE003"),
            ("Arjun", "Menon", "CSE", 5, 90.0, "2023CSE004"),
            ("Ishita", "Rao", "CSE", 5, 68.0, "2023CSE005"),
            ("Karan", "Shah", "CSE", 5, 82.5, "2023CSE006"),
            ("Manish", "Mishra", "CSE", 7, 80.5, "2022CSE001"),
            ("Pooja", "Dubey", "CSE", 7, 87.0, "2022CSE002"),
            ("Siddharth", "Jain", "CSE", 7, 75.0, "2022CSE003"),
            ("Tanvi", "Agarwal", "CSE", 7, 92.0, "2022CSE004"),
            ("Arjun", "Pillai", "IT", 3, 82.0, "2024IT001"),
            ("Divya", "Krishnan", "IT", 3, 90.5, "2024IT002"),
            ("Sanjay", "Iyer", "IT", 3, 58.0, "2024IT003"),
            ("Nisha", "Pillai", "IT", 3, 76.0, "2024IT004"),
            ("Varun", "Nambiar", "IT", 3, 70.5, "2024IT005"),
            ("Shreya", "Menon", "IT", 3, 85.0, "2024IT006"),
            ("Meera", "Joshi", "IT", 5, 76.0, "2023IT001"),
            ("Ravi", "Pillai", "IT", 5, 83.5, "2023IT002"),
            ("Akash", "Sharma", "IT", 5, 68.0, "2023IT003"),
            ("Kriti", "Bose", "IT", 5, 88.0, "2023IT004"),
            ("Neha", "Saxena", "IT", 7, 91.0, "2022IT001"),
            ("Pranav", "Deshmukh", "IT", 7, 79.0, "2022IT002"),
            ("Arun", "Rao", "ECE", 3, 79.5, "2024ECE001"),
            ("Lakshmi", "Iyer", "ECE", 3, 88.0, "2024ECE002"),
            ("Karthik", "Srinivasan", "ECE", 3, 42.0, "2024ECE003"),
            ("Bhavna", "Kulkarni", "ECE", 3, 74.0, "2024ECE004"),
            ("Rahul", "Hegde", "ECE", 3, 81.5, "2024ECE005"),
            ("Swathi", "Rao", "ECE", 3, 69.0, "2024ECE006"),
            ("Deepa", "Mahajan", "ECE", 5, 70.0, "2023ECE001"),
            ("Suresh", "Bhat", "ECE", 5, 85.5, "2023ECE002"),
            ("Harini", "Venkat", "ECE", 5, 77.0, "2023ECE003"),
            ("Vijay", "Raman", "ECE", 5, 62.0, "2023ECE004"),
            ("Asha", "Nambiar", "ECE", 7, 77.5, "2022ECE001"),
            ("Ganesh", "Murthy", "ECE", 7, 84.0, "2022ECE002"),
            ("Riya", "Shah", "ECE", 7, 90.0, "2022ECE003"),
            ("Aniket", "Joshi", "ECE", 7, 68.0, "2022ECE004"),
            ("Sanya", "Iyer", "ECE", 7, 82.0, "2022ECE005"),
        ]
        for first, last, dept, sem, attendance, enrollment in students_data:
            username = f"{first.lower()}.{last.lower()}"
            email = f"{enrollment.lower()}@university.edu"
            existing = CustomUser.objects.filter(username=username).first()
            if existing:
                username = f"{first.lower()}.{last.lower()}.{enrollment[-3:].lower()}"
            if CustomUser.objects.filter(username=username).exists():
                continue
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                password="student123",
                role="student",
            )
            Student.objects.create(
                user=user,
                enrollment_number=enrollment,
                department=dept,
                semester=sem,
                attendance=attendance,
            )
        self.stdout.write(f"  Created {len(students_data)} students")
    def create_marks(self):
        students = Student.objects.all()
        for student in students:
            subjects = Subject.objects.filter(
                department__in=[student.department, "GEN"],
                semester__lte=student.semester,
            )
            for subject in subjects:
                base = student.attendance * 0.6 
                variation = random.uniform(-15, 25)
                score = min(100, max(0, base + variation))
                if student.attendance > 85:
                    score = min(100, score + random.uniform(5, 15))
                elif student.attendance < 60:
                    score = max(0, score - random.uniform(10, 20))
                Marks.objects.update_or_create(
                    student=student,
                    subject=subject,
                    exam_type="END",
                    defaults={"score": round(score, 1)},
                )
        total_marks = Marks.objects.count()
        self.stdout.write(f"  Created {total_marks} marks entries")
    def create_performance_history(self):
        students = Student.objects.filter(semester__gte=3)
        for student in students:
            cgpa_track = []
            for sem in range(1, student.semester):
                if sem == 1:
                    sgpa = random.uniform(5.5, 8.5)
                else:
                    prev = cgpa_track[-1] if cgpa_track else 6.5
                    change = random.uniform(-0.5, 0.7)
                    sgpa = max(4.0, min(10.0, prev + change))
                cgpa_track.append(sgpa)
                cgpa = sum(cgpa_track) / len(cgpa_track)
                att = student.attendance + random.uniform(-10, 5)
                att = max(40, min(100, att))
                PerformanceHistory.objects.update_or_create(
                    student=student,
                    semester=sem,
                    defaults={
                        "sgpa": round(sgpa, 2),
                        "cgpa": round(cgpa, 2),
                        "attendance": round(att, 1),
                        "total_credits": random.randint(18, 24),
                    },
                )
        history_count = PerformanceHistory.objects.count()
        self.stdout.write(f"  Created {history_count} history records")
    def create_attendance_records(self):
        students = Student.objects.all()
        for student in students:
            for sem in range(1, student.semester + 1):
                subjects = Subject.objects.filter(
                    Q(department=student.department) | Q(department="GEN"), semester=sem
                )
                for subject in subjects:
                    total_classes = random.randint(40, 60)
                    base_attendance = student.attendance
                    variation = random.uniform(-10, 15)
                    attendance_pct = max(0, min(100, base_attendance + variation))
                    attended = int((attendance_pct / 100) * total_classes)
                    Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        semester=sem,
                        defaults={
                            "total_classes": total_classes,
                            "attended_classes": attended,
                        },
                    )
        attendance_count = Attendance.objects.count()
        self.stdout.write(f"  Created {attendance_count} attendance records")
    def generate_predictions(self):
        students = Student.objects.all()
        for student in students:
            Prediction.generate_prediction(student)
        self.stdout.write(f"  Generated predictions for {students.count()} students")
    def create_timetable(self):
        TimeSlot.objects.all().delete()
        time_slots = [
            (time(9, 0), time(10, 0)),    
            (time(10, 0), time(11, 0)),   
            (time(11, 15), time(12, 15)), 
            (time(12, 15), time(13, 15)), 
        ]
        lab_slot = (time(14, 0), time(16, 0))
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        rooms = ["Room 101", "Room 102", "Room 103", "Room 201", "Room 202"]
        lab_rooms = ["Lab 1", "Lab 2", "Lab 3", "Lab 4"]
        departments = ["CSE", "IT", "ECE"]
        semesters_to_create = [1, 3, 5, 7] 
        created_count = 0
        for dept in departments:
            teachers = list(Teacher.objects.filter(department=dept))
            if not teachers:
                continue
            for semester in semesters_to_create:
                subjects = list(
                    Subject.objects.filter(department=dept, semester=semester)
                )
                if not subjects:
                    continue
                theory_subjects = [s for s in subjects if not s.is_lab]
                lab_subjects = [s for s in subjects if s.is_lab]
                for idx, subject in enumerate(theory_subjects):
                    day = days[idx % len(days)]
                    period = idx % len(time_slots)
                    start_time, end_time = time_slots[period]
                    room = rooms[idx % len(rooms)]
                    teacher = teachers[idx % len(teachers)] if teachers else None
                    TimeSlot.objects.get_or_create(
                        subject=subject,
                        day_of_week=day,
                        start_time=start_time,
                        semester=semester,
                        defaults={
                            "faculty": teacher.user if teacher else None,
                            "end_time": end_time,
                            "room_number": room,
                            "department": dept,
                        }
                    )
                    created_count += 1
                for idx, subject in enumerate(lab_subjects):
                    day = days[idx % len(days)]
                    teacher = teachers[idx % len(teachers)] if teachers else None
                    lab_room = lab_rooms[idx % len(lab_rooms)]
                    TimeSlot.objects.get_or_create(
                        subject=subject,
                        day_of_week=day,
                        start_time=lab_slot[0],
                        semester=semester,
                        defaults={
                            "faculty": teacher.user if teacher else None,
                            "end_time": lab_slot[1],
                            "room_number": lab_room,
                            "department": dept,
                        }
                    )
                    created_count += 1
        timetable_count = TimeSlot.objects.count()
        self.stdout.write(f"  Created {timetable_count} timetable entries")
    def print_login_credentials(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("LOGIN CREDENTIALS"))
        self.stdout.write("=" * 60)
        self.stdout.write("\n" + "-" * 40)
        self.stdout.write(self.style.WARNING("ADMIN"))
        self.stdout.write("-" * 40)
        self.stdout.write("  Username: admin")
        self.stdout.write("  Password: admin123")
        self.stdout.write("\n" + "-" * 40)
        self.stdout.write(self.style.WARNING("TEACHERS (Password: prof123)"))
        self.stdout.write("-" * 40)
        teachers = Teacher.objects.select_related("user").all()
        for teacher in teachers:
            self.stdout.write(
                f"  {teacher.user.get_full_name():25} | {teacher.user.username:20} | {teacher.department}"
            )
        self.stdout.write("\n" + "-" * 40)
        self.stdout.write(self.style.WARNING("STUDENTS (Password: student123)"))
        self.stdout.write("-" * 40)
        for dept in ["CSE", "IT", "ECE"]:
            students = (
                Student.objects.filter(department=dept)
                .select_related("user")
                .order_by("semester", "enrollment_number")
            )
            if students:
                self.stdout.write(f"\n  {dept} Department:")
                for student in students:
                    self.stdout.write(
                        f"    {student.user.get_full_name():20} | {student.user.username:25} | Sem {student.semester}"
                    )
        self.stdout.write("\n" + "=" * 60 + "\n")
