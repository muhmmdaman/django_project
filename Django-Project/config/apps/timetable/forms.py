from django import forms
from django.contrib.auth import get_user_model
from .models import TimeSlot
from students.models import Subject
User = get_user_model()
class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = [
            "subject",
            "faculty",
            "day_of_week",
            "start_time",
            "end_time",
            "room_number",
            "department",
            "semester",
        ]
        widgets = {
            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "faculty": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "day_of_week": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "room_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Room 101, Lab 3",
                }
            ),
            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "semester": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 8,
                }
            ),
        }
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
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["faculty"].queryset = User.objects.filter(role="teacher")
        self.fields["faculty"].required = False
        self.fields["subject"].label = "Subject"
        self.fields["faculty"].label = "Faculty (Optional)"
        self.fields["day_of_week"].label = "Day"
        self.fields["start_time"].label = "Start Time"
        self.fields["end_time"].label = "End Time"
        self.fields["room_number"].label = "Room / Lab"
        self.fields["department"].label = "Department"
        self.fields["semester"].label = "Semester"
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time.")
        return cleaned_data
class TimetableFilterForm(forms.Form):
    DEPARTMENT_CHOICES = [("", "All Departments")] + [
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
    SEMESTER_CHOICES = [("", "All Semesters")] + [
        (str(i), f"Semester {i}") for i in range(1, 9)
    ]
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select form-select-sm",
                "onchange": "this.form.submit()",
            }
        ),
    )
    semester = forms.ChoiceField(
        choices=SEMESTER_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select form-select-sm",
                "onchange": "this.form.submit()",
            }
        ),
    )
