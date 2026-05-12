"""Management command to populate timetable from Excel file.
Parses the Jaypee University timetable Excel file.
"""
import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from timetable.models import TimeSlot
from students.models import Subject
from accounts.models import CustomUser
import re
from datetime import time
class Command(BaseCommand):
    help = "Populate timetable from Excel file"
    TIME_SLOTS = {
        "9 - 9:55": ("09:00", "09:55"),
        "9 - 9:55 ": ("09:00", "09:55"),
        "10 - 10:55": ("10:00", "10:55"),
        "10 - 10:55 ": ("10:00", "10:55"),
        "11:10 - 12:05": ("11:10", "12:05"),
        "11:10 - 12:05 ": ("11:10", "12:05"),
        "12:10 - 01:05": ("12:10", "13:05"),
        "12:10 - 01:05 ": ("12:10", "13:05"),
        "1:05 - 2:05": ("13:05", "14:05"),
        "1:05 - 2:05 ": ("13:05", "14:05"),
        "2:05 - 03:00": ("14:05", "15:00"),
        "2:05 - 03:00 ": ("14:05", "15:00"),
        "3:05 - 04:00": ("15:05", "16:00"),
        "3:05 - 04:00 ": ("15:05", "16:00"),
        "4:05 - 05:00": ("16:05", "17:00"),
        "4:05 - 05:00 ": ("16:05", "17:00"),
        "9:00 - 9:55": ("09:00", "09:55"),
        "10:00 - 10:55": ("10:00", "10:55"),
    }
    DAY_MAPPING = {
        "Mon": "monday",
        "Monday": "monday",
        "Tue": "tuesday",
        "Tue day": "tuesday",
        "Tuesday": "tuesday",
        "Wed": "wednesday",
        "Wednesday": "wednesday",
        "Thu": "thursday",
        "Thursday": "thursday",
        "Fri": "friday",
        "Friday": "friday",
        "Sat": "saturday",
        "Saturday": "saturday",
    }
    PROGRAM_DEPT_MAP = {
        "BBA": ("BBA", 2),
        "B.Com": ("BBA", 2),
        "MBA": ("MBA", 2),
        "BCA": ("BCA", 2),
        "BCA 2nd sem": ("BCA", 2),
        "BCA 4rth sem": ("BCA", 4),
        "BCA 6th sem": ("BCA", 6),
        "MCA": ("MCA", 2),
        "MCA 2nd sem": ("MCA", 2),
        "MCA 4rth sem": ("MCA", 4),
        "MCA 4rth Semester": ("MCA", 4),
        "B. Tech": ("CSE", 2),
        "B.Tech": ("CSE", 2),
        "BTech": ("CSE", 2),
        "BA": ("BA", 2),
        "BA 2nd": ("BA", 2),
        "BA 4th": ("BA", 4),
        "BA 6th": ("BA", 6),
        "BSc": ("BSc", 2),
        "BSc 2nd": ("BSc", 2),
        "BSc 4th": ("BSc", 4),
        "BSc 6th": ("BSc", 6),
        "ZBC": ("BSc", 2),
    }
    def add_arguments(self, parser):
        parser.add_argument(
            "excel_path",
            nargs="?",
            default=r"c:\Users\DELL\Downloads\Time Table Effective from 2 Feb 2026.xlsx",
            help="Path to Excel file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing timetable before importing",
        )
    def handle(self, *args, **options):
        excel_path = options["excel_path"]
        if options["clear"]:
            self.stdout.write("Clearing existing timetable entries...")
            TimeSlot.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Cleared all timetable entries"))
        try:
            self.import_timetable(excel_path)
            self.stdout.write(
                self.style.SUCCESS("[OK] Timetable imported successfully!")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] {str(e)}"))
            import traceback
            traceback.print_exc()
    def import_timetable(self, excel_path):
        xls = pd.ExcelFile(excel_path)
        sheets_to_process = ["BBA-MBA-BCom", "BCA-MCA", "BTech", "BA", "BSc"]
        total_slots = 0
        for sheet in sheets_to_process:
            if sheet not in xls.sheet_names:
                self.stdout.write(f"[SKIP] Sheet '{sheet}' not found, skipping...")
                continue
            self.stdout.write(f"\n[INFO] Processing {sheet}...")
            df = pd.read_excel(excel_path, sheet_name=sheet)
            slot_count = self._parse_sheet(df, sheet)
            total_slots += slot_count
            self.stdout.write(self.style.SUCCESS(f"   [OK] Added {slot_count} slots"))
        self.stdout.write(f"\n[STATS] Total slots added: {total_slots}")
    def _parse_sheet(self, df, sheet_name):
        slots_added = 0
        header_row = None
        for idx, row in df.iterrows():
            row_str = str(row.values).lower()
            if "9 - 9:55" in row_str or "9:00" in row_str:
                header_row = idx
                break
        if header_row is None:
            return 0
        header = df.iloc[header_row]
        time_slot_columns = []
        for col_idx, val in enumerate(header):
            if pd.notna(val):
                col_val = str(val).strip()
                if any(ts in col_val for ts in self.TIME_SLOTS.keys()):
                    time_slot_columns.append((col_idx, col_val))
        for idx in range(header_row + 1, len(df)):
            row = df.iloc[idx]
            day_val = row.iloc[0]
            if pd.isna(day_val):
                continue
            day_str = str(day_val).strip()
            if day_str not in self.DAY_MAPPING:
                continue
            day = self.DAY_MAPPING[day_str]
            prog_sem = str(row.iloc[1] if len(row) > 1 else "").strip()
            if not prog_sem or prog_sem == "nan":
                continue
            dept, sem = self._get_dept_semester(prog_sem)
            if not dept:
                continue
            for col_idx, time_slot_str in time_slot_columns:
                if col_idx >= len(row):
                    continue
                cell_value = row.iloc[col_idx]
                if pd.isna(cell_value):
                    continue
                cell_str = str(cell_value).strip()
                if not cell_str or cell_str.lower() in [
                    "nan",
                    "lunch",
                    "self study",
                    "library",
                    "project",
                ]:
                    continue
                slot_data = self._parse_cell(cell_str, day, time_slot_str, dept, sem)
                if slot_data:
                    slots_added += 1
                    if not self._slot_exists(slot_data):
                        TimeSlot.objects.create(**slot_data)
        return slots_added
    def _get_dept_semester(self, prog_sem):
        prog_sem = str(prog_sem).strip()
        for key, (dept, sem) in self.PROGRAM_DEPT_MAP.items():
            if key in prog_sem:
                match = re.search(r"(\d+)(nd|rd|th|st) sem", prog_sem)
                if match:
                    sem = int(match.group(1))
                return dept, sem
        return None, None
    def _parse_cell(self, cell_str, day, time_slot_str, dept, semester):
        match = re.match(
            r"[LTP]:([A-Z0-9]+)\s*\(([A-Z]{1,3})\)\s*([A-Z0-9\-]+)?", cell_str
        )
        if not match:
            return None
        course_code = match.group(1)
        faculty_initials = match.group(2)
        room = match.group(3) if match.group(3) else ""
        try:
            subject = Subject.objects.get(code=course_code)
        except Subject.DoesNotExist:
            subject = Subject.objects.create(
                name=course_code,
                code=course_code,
                department=dept,
                semester=semester,
                credits=3,
                is_lab="lab" in cell_str.lower() or "P:" in cell_str,
            )
        faculty = None
        try:
            faculty = CustomUser.objects.filter(
                role="teacher",
                first_name__startswith=faculty_initials[0] if faculty_initials else "",
            ).first()
        except:
            pass
        start_time_str, end_time_str = self.TIME_SLOTS.get(
            time_slot_str, ("09:00", "09:55")
        )
        start_time = timezone.datetime.strptime(start_time_str, "%H:%M").time()
        end_time = timezone.datetime.strptime(end_time_str, "%H:%M").time()
        return {
            "subject": subject,
            "faculty": faculty,
            "day_of_week": day,
            "start_time": start_time,
            "end_time": end_time,
            "room_number": room,
            "department": dept,
            "semester": semester,
        }
    def _slot_exists(self, slot_data):
        return TimeSlot.objects.filter(
            subject=slot_data["subject"],
            day_of_week=slot_data["day_of_week"],
            start_time=slot_data["start_time"],
            semester=slot_data["semester"],
        ).exists()
