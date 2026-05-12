from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
class Subject(models.Model):
    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics & Communication"),
        ("EEE", "Electrical & Electronics"),
        ("ME", "Mechanical Engineering"),
        ("CE", "Civil Engineering"),
        ("BBA", "Bachelor of Business Administration"),
        ("MBA", "Master of Business Administration"),
        ("BCA", "Bachelor of Computer Applications"),
        ("MCA", "Master of Computer Applications"),
        ("BA", "Bachelor of Arts"),
        ("BSc", "Bachelor of Science"),
        ("BTech", "Bachelor of Technology"),
        ("GEN", "General (All Departments)"),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.CharField(
        max_length=10,
        choices=DEPARTMENT_CHOICES,
        default="GEN",
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        default=1,
    )
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=3,
    )
    is_lab = models.BooleanField(
        default=False,
        help_text="True if this is a lab/practical subject",
    )
    class Meta:
        ordering = ["department", "semester", "name"]
        unique_together = ["code", "department"]
    def __str__(self):
        return f"{self.code} - {self.name}"
class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics & Communication"),
        ("EEE", "Electrical & Electronics"),
        ("ME", "Mechanical Engineering"),
        ("CE", "Civil Engineering"),
        ("BBA", "Bachelor of Business Administration"),
        ("MBA", "Master of Business Administration"),
        ("BCA", "Bachelor of Computer Applications"),
        ("MCA", "Master of Computer Applications"),
        ("BA", "Bachelor of Arts"),
        ("BSc", "Bachelor of Science"),
        ("BTech", "Bachelor of Technology"),
    ]
    CLASS_CHOICES = [
        ("CSE", "Computer Science"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics"),
        ("EEE", "Electrical"),
        ("ME", "Mechanical"),
        ("CE", "Civil"),
        ("BBA", "BBA"),
        ("MBA", "MBA"),
        ("BCA", "BCA"),
        ("MCA", "MCA"),
        ("BA", "BA"),
        ("BSc", "BSc"),
        ("BTech", "BTech"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    enrollment_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        default="",
        help_text="Unique enrollment/registration number",
    )
    department = models.CharField(
        max_length=10, choices=DEPARTMENT_CHOICES, default="CSE"
    )
    class_name = models.CharField(
        max_length=10, choices=CLASS_CHOICES, default="CSE"
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        default=1,
    )
    attendance = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Attendance percentage (0-100)",
    )
    cgpa = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Cumulative Grade Point Average (0-10)",
    )
    enrolled_date = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ["-enrolled_date", "user__first_name"]
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.enrollment_number})"
    def save(self, *args, **kwargs):
        self.class_name = self.department
        super().save(*args, **kwargs)
    def get_class_name_display(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)
    def get_average_marks(self):
        marks = self.marks.all()
        if marks.exists():
            return round(marks.aggregate(avg=models.Avg("score"))["avg"], 2)
        return 0.0
    def calculate_cgpa(self):
        marks_qs = self.marks.select_related("subject").all()
        if not marks_qs.exists():
            return 0.0
        total_credits = 0
        total_grade_points = 0
        for mark in marks_qs:
            credits = mark.subject.credits
            grade_point = self.score_to_grade_point(mark.score)
            total_credits += credits
            total_grade_points += grade_point * credits
        if total_credits == 0:
            return 0.0
        cgpa = total_grade_points / total_credits
        return round(cgpa, 2)
    def calculate_sgpa(self, semester):
        from django.db.models import Q
        semester_subjects = Subject.objects.filter(
            Q(department=self.department) | Q(department="GEN"), semester=semester
        )
        marks_qs = self.marks.filter(subject__in=semester_subjects).select_related(
            "subject"
        )
        if not marks_qs.exists():
            return 0.0
        total_credits = 0
        total_grade_points = 0
        for mark in marks_qs:
            credits = mark.subject.credits
            grade_point = self.score_to_grade_point(mark.score)
            total_credits += credits
            total_grade_points += grade_point * credits
        if total_credits == 0:
            return 0.0
        sgpa = total_grade_points / total_credits
        return round(sgpa, 2)
    def get_semester_attendance(self, semester):
        attendance_records = self.attendance_records.filter(semester=semester)
        if not attendance_records.exists():
            return self.attendance
        total_classes = (
            attendance_records.aggregate(total=models.Sum("total_classes"))["total"]
            or 0
        )
        attended_classes = (
            attendance_records.aggregate(attended=models.Sum("attended_classes"))[
                "attended"
            ]
            or 0
        )
        if total_classes == 0:
            return 0.0
        return round((attended_classes / total_classes) * 100, 2)
    @staticmethod
    def score_to_grade_point(score):
        if score >= 90:
            return 10.0
        elif score >= 80:
            return 9.0
        elif score >= 70:
            return 8.0
        elif score >= 60:
            return 7.0
        elif score >= 55:
            return 6.0
        elif score >= 50:
            return 5.0
        elif score >= 45:
            return 4.0
        else:
            return 0.0
    @staticmethod
    def grade_point_to_grade(gp):
        if gp >= 9.5:
            return "O", "Outstanding"
        elif gp >= 8.5:
            return "A+", "Excellent"
        elif gp >= 7.5:
            return "A", "Very Good"
        elif gp >= 6.5:
            return "B+", "Good"
        elif gp >= 5.5:
            return "B", "Above Average"
        elif gp >= 4.5:
            return "C", "Average"
        elif gp >= 4.0:
            return "P", "Pass"
        else:
            return "F", "Fail"
    def get_grade_classification(self):
        cgpa = self.cgpa or self.calculate_cgpa()
        if cgpa >= 8.5:
            return "Excellent", "success"
        elif cgpa >= 7.0:
            return "Good", "primary"
        elif cgpa >= 5.0:
            return "Average", "warning"
        else:
            return "Poor", "danger"
    def get_weakest_subjects(self, limit=3):
        marks = self.marks.select_related("subject").order_by("score")[:limit]
        return [(m.subject, m.score) for m in marks if m.score < 60]
    def get_strongest_subjects(self, limit=3):
        return self.marks.select_related("subject").order_by("-score")[:limit]
class Marks(models.Model):
    EXAM_TYPE_CHOICES = [
        ("MID1", "Mid Semester 1"),
        ("MID2", "Mid Semester 2"),
        ("END", "End Semester"),
        ("INTERNAL", "Internal Assessment"),
    ]
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="marks",
    )
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Score out of 100",
    )
    exam_type = models.CharField(
        max_length=10,
        choices=EXAM_TYPE_CHOICES,
        default="END",
    )
    exam_date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Marks"
        verbose_name_plural = "Marks"
        unique_together = ["student", "subject", "exam_type"]
        ordering = ["-exam_date", "student", "subject"]
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.subject.code}: {self.score}"
    def get_grade(self):
        gp = Student.score_to_grade_point(self.score)
        grade, _ = Student.grade_point_to_grade(gp)
        return grade
    def get_grade_point(self):
        return Student.score_to_grade_point(self.score)
class PerformanceHistory(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="performance_history",
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    sgpa = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Semester Grade Point Average",
    )
    cgpa = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Cumulative Grade Point Average at this point",
    )
    attendance = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    total_credits = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["student", "semester"]
        unique_together = ["student", "semester"]
        verbose_name_plural = "Performance Histories"
    def __str__(self):
        return (
            f"{self.student.enrollment_number} - Sem {self.semester}: SGPA {self.sgpa}"
        )
class Teacher(models.Model):
    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics & Communication"),
        ("EEE", "Electrical & Electronics"),
        ("ME", "Mechanical Engineering"),
        ("CE", "Civil Engineering"),
        ("BBA", "Bachelor of Business Administration"),
        ("MBA", "Master of Business Administration"),
        ("BCA", "Bachelor of Computer Applications"),
        ("MCA", "Master of Computer Applications"),
        ("BA", "Bachelor of Arts"),
        ("BSc", "Bachelor of Science"),
        ("BTech", "Bachelor of Technology"),
    ]
    SALARY_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("due", "Due"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique employee/faculty ID",
    )
    department = models.CharField(
        max_length=10, choices=DEPARTMENT_CHOICES, default="CSE"
    )
    designation = models.CharField(
        max_length=50,
        default="Assistant Professor",
        help_text="e.g., Professor, Assistant Professor, Lecturer",
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="teachers",
        blank=True,
        help_text="Subjects taught by this teacher",
    )
    phone = models.CharField(max_length=15, blank=True)
    joined_date = models.DateField(auto_now_add=True)
    salary_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Monthly salary in INR",
    )
    salary_status = models.CharField(
        max_length=10,
        choices=SALARY_STATUS_CHOICES,
        default="due",
        help_text="Payment status: paid or due",
    )
    last_paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last salary payment",
    )
    next_payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled next payment date",
    )
    payment_notes = models.TextField(
        blank=True,
        help_text="Additional notes about salary/payments",
    )
    class Meta:
        ordering = ["department", "user__first_name"]
        verbose_name_plural = "Teachers"
        indexes = [
            models.Index(fields=["salary_status"]),
            models.Index(fields=["last_paid_date"]),
        ]
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.department})"
    def is_salary_due(self):
        return self.salary_status == "due"
    def mark_salary_paid(self, paid_date=None):
        from django.utils import timezone
        self.salary_status = "paid"
        self.last_paid_date = paid_date or timezone.now().date()
        self.save(update_fields=["salary_status", "last_paid_date"])
    def get_salary_status_display(self):
        status_dict = {
            "paid": "Paid",
            "due": "Due",
        }
        return status_dict.get(self.salary_status, self.salary_status)
class SalaryPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("check", "Check"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="salary_payments",
        help_text="Teacher receiving payment",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount paid in INR",
    )
    payment_date = models.DateField(
        help_text="Date of payment",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="bank_transfer",
        help_text="Method of payment",
    )
    reference_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Bank reference, check number, or transaction ID",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_salary_payments",
        help_text="Admin who processed this payment",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this payment",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this payment record was created",
    )
    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Salary Payment"
        verbose_name_plural = "Salary Payments"
        indexes = [
            models.Index(fields=["teacher", "-payment_date"]),
            models.Index(fields=["payment_date"]),
        ]
    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - ₹{self.amount} on {self.payment_date}"
class TeacherSubjectAssignmentDocument(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="subject_assignment_documents",
        help_text="Teacher uploading the document",
    )
    document = models.FileField(
        upload_to="teacher_documents/%Y/%m/%d/",
        help_text="Assignment letter or documentation",
    )
    document_name = models.CharField(
        max_length=255,
        help_text="Name/title of the document",
    )
    subjects = models.ManyToManyField(
        Subject,
        help_text="Subjects to be assigned based on this document",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Approval status of the document",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the document was uploaded",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_teacher_documents",
        help_text="Admin who approved this document",
    )
    approval_notes = models.TextField(
        blank=True,
        help_text="Notes from admin during approval/rejection",
    )
    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Teacher Subject Assignment Document"
        verbose_name_plural = "Teacher Subject Assignment Documents"
        indexes = [
            models.Index(fields=["teacher", "-uploaded_at"]),
            models.Index(fields=["status"]),
        ]
    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.document_name} ({self.status})"
    def approve(self, approved_by, notes=""):
        self.status = "approved"
        self.approved_by = approved_by
        self.approval_notes = notes
        self.save()
        for subject in self.subjects.all():
            self.teacher.subjects.add(subject)
    def reject(self, approved_by, reason=""):
        self.status = "rejected"
        self.approved_by = approved_by
        self.approval_notes = reason
        self.save()
class Attendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True,
        help_text="Optional: Track attendance per subject",
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    total_classes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total classes conducted",
    )
    attended_classes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Classes attended by student",
    )
    percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Attendance percentage (auto-calculated)",
    )
    recorded_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["student", "semester", "subject"]
        unique_together = ["student", "semester", "subject"]
        verbose_name_plural = "Attendance Records"
    def save(self, *args, **kwargs):
        if self.total_classes > 0:
            self.percentage = round(
                (self.attended_classes / self.total_classes) * 100, 2
            )
        else:
            self.percentage = 0.0
        super().save(*args, **kwargs)
    def __str__(self):
        subject_info = f" - {self.subject.code}" if self.subject else ""
        return f"{self.student.enrollment_number} - Sem {self.semester}{subject_info}: {self.percentage}%"
