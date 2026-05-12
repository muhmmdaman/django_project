from django import forms
from django.core.validators import FileExtensionValidator
from .models import (
    Student,
    Marks,
    Subject,
    TeacherSubjectAssignmentDocument,
    Teacher,
    SalaryPayment,
)
class StudentForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    enrollment_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., 2024CSE001"}
        ),
    )
    class Meta:
        model = Student
        fields = ["enrollment_number", "department", "semester", "attendance"]
        widgets = {
            "department": forms.Select(attrs={"class": "form-control"}),
            "semester": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 8,
                }
            ),
            "attendance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Attendance %",
                    "min": 0,
                    "max": 100,
                    "step": "0.1",
                }
            ),
        }
    def clean_enrollment_number(self):
        enrollment = self.cleaned_data.get("enrollment_number")
        if Student.objects.filter(enrollment_number=enrollment).exists():
            if not self.instance or self.instance.enrollment_number != enrollment:
                raise forms.ValidationError("This enrollment number already exists.")
        return enrollment
class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ["student", "subject", "score", "exam_type"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "subject": forms.Select(attrs={"class": "form-control"}),
            "score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Score (0-100)",
                    "min": 0,
                    "max": 100,
                    "step": "0.1",
                }
            ),
            "exam_type": forms.Select(attrs={"class": "form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.select_related("user")
        self.fields["subject"].queryset = Subject.objects.all().order_by("code")
    def clean_score(self):
        score = self.cleaned_data.get("score")
        if score is not None and (score < 0 or score > 100):
            raise forms.ValidationError("Score must be between 0 and 100.")
        return score
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".csv",
            }
        ),
        help_text="Upload a CSV file with the required columns.",
    )
class StudentCSVUploadForm(CSVUploadForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["csv_file"].help_text = (
            "Required columns: first_name, last_name, email, enrollment_number, "
            "department, semester, attendance"
        )
class MarksCSVUploadForm(CSVUploadForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["csv_file"].help_text = (
            "Required columns: enrollment_number, subject_code, score, exam_type (optional)"
        )
class StudentFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by name or enrollment...",
            }
        ),
    )
    department = forms.ChoiceField(
        required=False,
        choices=[("", "All Departments")] + list(Student.DEPARTMENT_CHOICES),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    semester = forms.ChoiceField(
        required=False,
        choices=[("", "All Semesters")] + [(i, f"Semester {i}") for i in range(1, 9)],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    risk_level = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Risk Levels"),
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
            ("critical", "Critical Risk"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
class TeacherSubjectAssignmentDocumentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignmentDocument
        fields = ["document_name", "document", "subjects"]
        widgets = {
            "document_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Subject Assignment Letter Feb 2026",
                }
            ),
            "document": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.txt",
                }
            ),
            "subjects": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
        }
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher", None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields["subjects"].queryset = Subject.objects.filter(
                department=teacher.department
            ).order_by("code")
        else:
            self.fields["subjects"].queryset = Subject.objects.all().order_by("code")
class TeacherSubjectAssignmentApprovalForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignmentDocument
        fields = ["status", "approval_notes"]
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"},
                choices=[
                    ("approved", "Approve"),
                    ("rejected", "Reject"),
                ],
            ),
            "approval_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add approval or rejection notes...",
                }
            ),
        }
class TeacherSalaryStatusForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["salary_status", "salary_amount", "next_payment_date", "payment_notes"]
        widgets = {
            "salary_status": forms.Select(
                attrs={"class": "form-control"},
                choices=Teacher.SALARY_STATUS_CHOICES,
            ),
            "salary_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Monthly salary amount in INR",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "next_payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "payment_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes about salary/payments",
                }
            ),
        }
class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = ["amount", "payment_date", "payment_method", "reference_number", "notes"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Amount paid in INR",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "payment_method": forms.Select(
                attrs={"class": "form-control"},
                choices=SalaryPayment.PAYMENT_METHOD_CHOICES,
            ),
            "reference_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bank reference, check number, or transaction ID",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes about this payment",
                }
            ),
        }
