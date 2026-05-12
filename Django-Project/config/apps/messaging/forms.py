from django import forms
from django.core.exceptions import ValidationError
from .models import Message
from accounts.models import CustomUser
from students.models import Student
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["receiver", "content"]
        widgets = {
            "receiver": forms.Select(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Type your message...",
                }
            ),
        }
class BroadcastMessageForm(forms.Form):
    department = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select a department (leave empty for global broadcast)",
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Type your broadcast message...",
            }
        ),
        required=True,
        max_length=5000,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from students.models import Student
        departments = (
            Student.objects.values_list("department", flat=True)
            .distinct()
            .order_by("department")
        )
        self.fields["department"].choices = [
            ("", "All Departments (Global Broadcast)"),
        ] + [(d, d) for d in departments]
    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise ValidationError("Message content cannot be empty.")
        return content
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Type your reply...",
                }
            ),
        }
class BroadcastForm(forms.Form):
    RECIPIENT_CHOICES = [
        ("all_users", "All Users"),
        ("department", "Specific Department"),
        ("custom", "Custom Recipients"),
    ]
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Type your broadcast message...",
            }
        ),
        required=True,
        help_text="The message content to broadcast",
    )
    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Choose who should receive this broadcast",
    )
    department = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text='Select department (only if recipient type is "Specific Department")',
    )
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        departments = Student.objects.values_list("department", flat=True).distinct()
        self.fields["department"].choices = [
            ("", "--- Select Department ---"),
        ] + [(d, d) for d in departments]
        if user and user.role not in ["teacher", "admin"]:
            raise ValidationError("Only teachers and admins can send broadcasts.")
    def clean(self):
        cleaned_data = super().clean()
        recipient_type = cleaned_data.get("recipient_type")
        department = cleaned_data.get("department")
        if recipient_type == "department" and not department:
            raise ValidationError(
                'Department is required when recipient type is "Specific Department".'
            )
        return cleaned_data
class DepartmentBroadcastForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Type your broadcast message...",
            }
        ),
        required=True,
        help_text="The message content for your department",
    )
    target_department = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select the target department",
    )
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        departments = Student.objects.values_list("department", flat=True).distinct()
        self.fields["target_department"].choices = [
            ("", "--- Select Department ---"),
        ] + [(d, d) for d in departments]
        if user and user.role not in ["teacher", "admin"]:
            raise ValidationError(
                "Only teachers and admins can send department broadcasts."
            )
class GlobalBroadcastForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Type your global broadcast message...",
            }
        ),
        required=True,
        help_text="This message will be sent to ALL active users in the system",
    )
    confirm_broadcast = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="I understand this will be sent to all users in the system",
    )
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.role != "admin":
            raise ValidationError("Only admins can send global broadcasts.")
class AdminUserActionForm(forms.Form):
    ACTION_CHOICES = [
        ("ban", "Ban User"),
        ("mute", "Mute User"),
        ("unban", "Unban User"),
        ("unmute", "Unmute User"),
    ]
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        help_text="Choose the action to take",
    )
    reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Reason for this action...",
            }
        ),
        required=False,
        help_text="Reason is required for ban/mute actions",
    )
    expiration_days = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Leave empty for permanent action",
            }
        ),
        help_text="Number of days until restriction expires",
    )
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        reason = cleaned_data.get("reason")
        if action in ["ban", "mute"] and not reason:
            raise ValidationError("Reason is required for ban/mute actions.")
        return cleaned_data
class MessageFilterForm(forms.Form):
    VIEW_CHOICES = [
        ("all", "All Messages"),
        ("private", "Private Messages"),
        ("broadcast", "Broadcasts"),
        ("department", "Department Broadcasts"),
    ]
    view_type = forms.ChoiceField(
        choices=VIEW_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        initial="all",
    )
    date_from = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        required=False,
        help_text="Filter messages from this date onwards",
    )
    date_to = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        required=False,
        help_text="Filter messages up to this date",
    )
    is_deleted = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Show deleted messages (admin only)",
    )
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise ValidationError("Start date must be before end date.")
class TeacherCreationForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        required=True,
    )
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Employee ID"}
        ),
        required=True,
    )
    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics & Communication"),
        ("EEE", "Electrical & Electronics"),
        ("ME", "Mechanical Engineering"),
        ("CE", "Civil Engineering"),
        ("MBA", "Business Administration"),
    ]
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    designation = forms.CharField(
        max_length=50,
        initial="Assistant Professor",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Designation"}
        ),
        required=True,
    )
    salary_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Monthly Salary (INR)",
                "step": "0.01",
            }
        ),
        required=True,
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
        required=True,
        help_text="Temporary password for teacher account",
    )
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already in use.")
        return email
    def clean_employee_id(self):
        from students.models import Teacher
        employee_id = self.cleaned_data.get("employee_id")
        if Teacher.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("Employee ID already in use.")
        return employee_id
class TeacherUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        required=False,
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"}),
        required=False,
    )
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
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    designation = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    salary_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        required=True,
    )
    salary_status = forms.ChoiceField(
        choices=SALARY_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        help_text="Update salary payment status",
    )
class SalaryPaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("check", "Check"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Amount (₹)", "step": "0.01"}
        ),
        required=True,
        min_value=0,
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    reference_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Bank Ref / Check No / Transaction ID (optional)",
            }
        ),
        required=False,
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Additional notes (optional)",
            }
        ),
        required=False,
    )
    salary_status = forms.ChoiceField(
        choices=[("paid", "Mark as Paid"), ("due", "Mark as Due")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        initial="paid",
        help_text="Update salary status after recording payment",
    )
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return amount
class TeacherSalaryStatusForm(forms.Form):
    SALARY_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("due", "Due"),
    ]
    salary_status = forms.ChoiceField(
        choices=SALARY_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Salary Status",
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional notes about status change",
            }
        ),
        required=False,
        label="Notes (optional)",
    )
class QuickSalaryPaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Amount (₹)", "step": "0.01"}
        ),
        required=True,
        min_value=0,
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
        label="Payment Date",
    )
    payment_method = forms.ChoiceField(
        choices=[
            ("bank_transfer", "Bank Transfer"),
            ("check", "Check"),
            ("cash", "Cash"),
            ("other", "Other"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Payment Method",
        initial="bank_transfer",
    )
    reference_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Reference / Check / Transaction ID",
            }
        ),
        required=False,
    )
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return amount
class TeacherFilterForm(forms.Form):
    DEPARTMENT_CHOICES = [
        ("", "All Departments"),
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics & Communication"),
        ("EEE", "Electrical & Electronics"),
        ("ME", "Mechanical Engineering"),
        ("CE", "Civil Engineering"),
        ("MBA", "Business Administration"),
    ]
    SALARY_STATUS_CHOICES = [
        ("", "All Statuses"),
        ("paid", "Paid"),
        ("due", "Due"),
    ]
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    salary_status = forms.ChoiceField(
        choices=SALARY_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Name, Email, or Employee ID",
            }
        ),
        required=False,
    )
