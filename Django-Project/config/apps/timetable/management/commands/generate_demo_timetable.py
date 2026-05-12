"""Management command to generate demo timetable for departments without data.
Creates realistic dummy timetables for IT, ECE, EEE, ME, CE departments.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from timetable.models import TimeSlot
from students.models import Subject
from accounts.models import CustomUser
from datetime import time
import random
class Command(BaseCommand):
    help = "Generate demo timetable for departments without data"
    DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    TIME_SLOTS = [
        (time(9, 0), time(9, 55)),
        (time(10, 0), time(10, 55)),
        (time(11, 10), time(12, 5)),
        (time(12, 10), time(13, 5)),
        (time(13, 5), time(14, 5)),
        (time(14, 5), time(15, 0)),
        (time(15, 5), time(16, 0)),
        (time(16, 5), time(17, 0)),
    ]
    DEPT_CONFIGS = {
        "IT": {
            "name": "Information Technology",
            "courses": {
                2: [
                    "DATA STRUCTURES",
                    "WEB DEVELOPMENT",
                    "DATABASE",
                    "OOP",
                    "NETWORKING",
                ],
                4: [
                    "CLOUD COMPUTING",
                    "CYBERSECURITY",
                    "ML BASICS",
                    "SYSTEMS DESIGN",
                    "DEVOPS",
                ],
                6: [
                    "AI APPLICATIONS",
                    "ADVANCED ML",
                    "BLOCKCHAIN",
                    "NEURAL NETWORKS",
                    "CAPSTONE",
                ],
            },
        },
        "ECE": {
            "name": "Electronics & Communication Engineering",
            "courses": {
                2: [
                    "CIRCUIT ANALYSIS",
                    "SIGNALS & SYSTEMS",
                    "DIGITAL LOGIC",
                    "ELECTROMAGNETICS",
                    "COMMUNICATION",
                ],
                4: [
                    "MICROPROCESSORS",
                    "VLSI DESIGN",
                    "ANTENNAS",
                    "RF CIRCUITS",
                    "SIGNAL PROCESSING",
                ],
                6: [
                    "WIRELESS COMMUNICATION",
                    "OPTICAL COMMUNICATION",
                    "EMBEDDED SYSTEMS",
                    "NETWORK DESIGN",
                    "CAPSTONE",
                ],
            },
        },
        "EEE": {
            "name": "Electrical & Electronics Engineering",
            "courses": {
                2: [
                    "AC CIRCUITS",
                    "DC CIRCUITS",
                    "MACHINES",
                    "POWER SYSTEMS",
                    "CONTROL SYSTEMS",
                ],
                4: [
                    "POWER ELECTRONICS",
                    "ELECTRICAL MACHINES",
                    "GENERATION & TRANSMISSION",
                    "PROTECTION",
                    "DRIVES",
                ],
                6: [
                    "RENEWABLE ENERGY",
                    "SMART GRIDS",
                    "POWER QUALITY",
                    "INDUSTRIAL AUTOMATION",
                    "CAPSTONE",
                ],
            },
        },
        "ME": {
            "name": "Mechanical Engineering",
            "courses": {
                2: [
                    "THERMODYNAMICS",
                    "MECHANICS OF SOLIDS",
                    "FLUID MECHANICS",
                    "HEAT TRANSFER",
                    "MANUFACTURING",
                ],
                4: [
                    "MACHINE DESIGN",
                    "VIBRATIONS",
                    "THERMAL ENGINEERING",
                    "HYDRAULICS",
                    "CAD/CAM",
                ],
                6: [
                    "TURBOMACHINERY",
                    "RENEWABLE ENERGY",
                    "ROBOTICS",
                    "AUTOMATION",
                    "CAPSTONE",
                ],
            },
        },
        "CE": {
            "name": "Civil Engineering",
            "courses": {
                2: [
                    "SURVEYING",
                    "BUILDING MATERIALS",
                    "STRUCTURAL MECHANICS",
                    "HYDRAULICS",
                    "ENVIRONMENTAL",
                ],
                4: [
                    "CONCRETE DESIGN",
                    "STRUCTURAL ANALYSIS",
                    "GEOTECHNICAL",
                    "WATER RESOURCES",
                    "TRANSPORTATION",
                ],
                6: [
                    "BRIDGE ENGINEERING",
                    "CONSTRUCTION MANAGEMENT",
                    "EARTHQUAKE ENGINEERING",
                    "SMART CITIES",
                    "CAPSTONE",
                ],
            },
        },
    }
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing demo timetable before generating",
        )
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(
                "Clearing existing timetable entries for IT, ECE, EEE, ME, CE..."
            )
            for dept in ["IT", "ECE", "EEE", "ME", "CE"]:
                TimeSlot.objects.filter(department=dept).delete()
            self.stdout.write(self.style.SUCCESS("[OK] Cleared demo timetable"))
        try:
            self.generate_demo_timetable()
            self.stdout.write(
                self.style.SUCCESS("[OK] Demo timetable generated successfully!")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] {str(e)}"))
            import traceback
            traceback.print_exc()
    def generate_demo_timetable(self):
        total_slots = 0
        for dept_code, dept_config in self.DEPT_CONFIGS.items():
            self.stdout.write(f"\n[INFO] Generating timetable for {dept_code}...")
            for semester in [2, 4, 6]:
                courses = dept_config["courses"].get(semester, [])
                slot_count = self._generate_semester_timetable(
                    dept_code, semester, courses
                )
                total_slots += slot_count
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   [OK] Added {slot_count} slots for {dept_code} Sem {semester}"
                    )
                )
        self.stdout.write(f"\n[STATS] Total demo slots added: {total_slots}")
    def _generate_semester_timetable(self, dept_code, semester, courses):
        slots_added = 0
        course_idx = 0
        for day_idx, day in enumerate(self.DAYS):
            courses_per_day = 2 if day_idx < 5 else 1
            for slot_idx in range(courses_per_day):
                if course_idx >= len(courses):
                    break
                course_name = courses[course_idx]
                time_slot_idx = (day_idx * 2 + slot_idx) % len(self.TIME_SLOTS)
                start_time, end_time = self.TIME_SLOTS[time_slot_idx]
                course_code = f"{dept_code}{semester}{course_idx:02d}"
                subject, _ = Subject.objects.get_or_create(
                    code=course_code,
                    defaults={
                        "name": course_name,
                        "department": dept_code,
                        "semester": semester,
                        "credits": 3,
                        "is_lab": "LAB" in course_name.upper(),
                    },
                )
                faculty = (
                    CustomUser.objects.filter(role="teacher").order_by("?").first()
                )
                room_num = f"A{100 + slot_idx}{day_idx}"
                if not TimeSlot.objects.filter(
                    subject=subject,
                    day_of_week=day,
                    start_time=start_time,
                    semester=semester,
                ).exists():
                    TimeSlot.objects.create(
                        subject=subject,
                        faculty=faculty,
                        day_of_week=day,
                        start_time=start_time,
                        end_time=end_time,
                        room_number=room_num,
                        department=dept_code,
                        semester=semester,
                    )
                    slots_added += 1
                course_idx += 1
            if course_idx >= len(courses):
                break
        return slots_added
