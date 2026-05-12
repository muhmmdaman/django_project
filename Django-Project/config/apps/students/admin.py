from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Subject, Marks, PerformanceHistory, Teacher, Attendance, SalaryPayment
class RiskLevelFilter(admin.SimpleListFilter):
    title = "Risk Level"
    parameter_name = "risk_level"
    def lookups(self, request, model_admin):
        return [
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
            ("critical", "Critical Risk"),
            ("none", "No Prediction"),
        ]
    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(prediction__isnull=True)
        elif self.value():
            return queryset.filter(prediction__risk_level=self.value())
        return queryset
class AttendanceRiskFilter(admin.SimpleListFilter):
    title = "Attendance Risk"
    parameter_name = "attendance_risk"
    def lookups(self, request, model_admin):
        return [
            ("critical", "Critical (< 60%)"),
            ("at_risk", "At Risk (< 75%)"),
            ("good", "Good (>= 75%)"),
        ]
    def queryset(self, request, queryset):
        if self.value() == "critical":
            return queryset.filter(attendance__lt=60)
        elif self.value() == "at_risk":
            return queryset.filter(attendance__lt=75, attendance__gte=60)
        elif self.value() == "good":
            return queryset.filter(attendance__gte=75)
        return queryset
class CGPAFilter(admin.SimpleListFilter):
    title = "CGPA Range"
    parameter_name = "cgpa_range"
    def lookups(self, request, model_admin):
        return [
            ("excellent", "Excellent (8.5+)"),
            ("good", "Good (7.0-8.5)"),
            ("average", "Average (5.0-7.0)"),
            ("poor", "Poor (< 5.0)"),
            ("none", "Not Calculated"),
        ]
    def queryset(self, request, queryset):
        if self.value() == "excellent":
            return queryset.filter(cgpa__gte=8.5)
        elif self.value() == "good":
            return queryset.filter(cgpa__gte=7.0, cgpa__lt=8.5)
        elif self.value() == "average":
            return queryset.filter(cgpa__gte=5.0, cgpa__lt=7.0)
        elif self.value() == "poor":
            return queryset.filter(cgpa__lt=5.0, cgpa__isnull=False)
        elif self.value() == "none":
            return queryset.filter(cgpa__isnull=True)
        return queryset
class MarksInline(admin.TabularInline):
    model = Marks
    extra = 0
    min_num = 0
    fields = ["subject", "score", "exam_type", "grade_display", "exam_date"]
    readonly_fields = ["exam_date", "grade_display"]
    @admin.display(description="Grade")
    def grade_display(self, obj):
        if obj.pk:
            gp = obj.get_grade_point()
            grade = obj.get_grade()
            color = "#2ecc71"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} ({:.1f})</span>',
                color, grade, gp
            )
        return "-"
class PerformanceHistoryInline(admin.TabularInline):
    model = PerformanceHistory
    extra = 0
    readonly_fields = ["semester", "sgpa", "cgpa", "attendance", "total_credits", "recorded_at"]
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "department", "semester", "credits"]
    list_filter = ["department", "semester"]
    search_fields = ["name", "code"]
    ordering = ["department", "semester", "code"]
    list_per_page = 30
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "enrollment_number",
        "get_full_name",
        "department",
        "semester",
        "attendance_display",
        "cgpa_display",
        "get_risk_level",
        "enrolled_date",
    ]
    list_filter = [
        "department",
        "semester",
        RiskLevelFilter,
        AttendanceRiskFilter,
        CGPAFilter,
        "enrolled_date",
    ]
    search_fields = [
        "enrollment_number",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]
    ordering = ["-enrolled_date", "enrollment_number"]
    inlines = [MarksInline, PerformanceHistoryInline]
    raw_id_fields = ["user"]
    list_per_page = 20
    readonly_fields = ["cgpa", "enrolled_date"]
    fieldsets = (
        ("User Account", {
            "fields": ("user",),
        }),
        ("Academic Information", {
            "fields": ("enrollment_number", "department", "semester"),
        }),
        ("Performance", {
            "fields": ("attendance", "cgpa"),
        }),
        ("System Info", {
            "fields": ("enrolled_date",),
            "classes": ("collapse",),
        }),
    )
    @admin.display(description="Student Name")
    def get_full_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        email = obj.user.email
        return format_html(
            '<strong>{}</strong><br><small style="color: #7f8c8d;">{}</small>',
            name, email
        )
    @admin.display(description="CGPA")
    def cgpa_display(self, obj):
        cgpa = obj.cgpa
        if cgpa is None:
            return format_html('<span style="color: #7f8c8d;">Not Calculated</span>')
        color = "#2ecc71"
        grade, desc = obj.grade_point_to_grade(cgpa)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span> <small>({} - {})</small>',
            color, cgpa, grade, desc
        )
    @admin.display(description="Attendance")
    def attendance_display(self, obj):
        color = "#2ecc71" if obj.attendance >= 75 else "#f39c12" if obj.attendance >= 60 else "#e74c3c"
        icon = "✓" if obj.attendance >= 75 else "!" if obj.attendance >= 60 else "✗"
        return format_html(
            '<span style="color: {};">{} {:.1f}%</span>',
            color, icon, obj.attendance
        )
    @admin.display(description="Risk Level")
    def get_risk_level(self, obj):
        try:
            pred = obj.prediction
            colors = {
                "low": "#2ecc71",
                "medium": "#f39c12",
                "high": "#e74c3c",
                "critical": "#c0392b"
            }
            color = colors.get(pred.risk_level, "#7f8c8d")
            return format_html(
                '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
                color, pred.get_risk_level_display()
            )
        except Exception:
            return format_html('<span style="color: #7f8c8d;">No Prediction</span>')
@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = [
        "get_enrollment",
        "get_student_name",
        "subject",
        "score_display",
        "grade_display",
        "exam_type",
        "exam_date",
    ]
    list_filter = ["subject__department", "subject", "exam_type", "exam_date"]
    search_fields = [
        "student__enrollment_number",
        "student__user__first_name",
        "student__user__last_name",
        "subject__code",
        "subject__name",
    ]
    ordering = ["-exam_date", "student__enrollment_number"]
    raw_id_fields = ["student"]
    list_per_page = 30
    @admin.display(description="Enrollment")
    def get_enrollment(self, obj):
        return obj.student.enrollment_number
    @admin.display(description="Student")
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    @admin.display(description="Score")
    def score_display(self, obj):
        color = "#2ecc71"
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{:.1f}</span>',
            color, obj.score
        )
    @admin.display(description="Grade")
    def grade_display(self, obj):
        gp = obj.get_grade_point()
        grade = obj.get_grade()
        return format_html('<strong>{}</strong> <small>({:.1f})</small>', grade, gp)
@admin.register(PerformanceHistory)
class PerformanceHistoryAdmin(admin.ModelAdmin):
    list_display = ["student", "semester", "sgpa", "cgpa", "attendance", "total_credits", "recorded_at"]
    list_filter = ["semester", "recorded_at"]
    search_fields = ["student__enrollment_number", "student__user__first_name"]
    ordering = ["student", "semester"]
    readonly_fields = ["recorded_at"]
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        "employee_id",
        "get_full_name",
        "department",
        "salary_status_display",
        "salary_amount_display",
        "last_paid_date_display",
        "joined_date",
    ]
    list_filter = ["department", "designation", "salary_status", "last_paid_date", "joined_date"]
    search_fields = [
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]
    ordering = ["department", "user__first_name"]
    raw_id_fields = ["user"]
    filter_horizontal = ["subjects"]
    list_per_page = 20
    readonly_fields = ["joined_date"]
    fieldsets = (
        ("User Account", {
            "fields": ("user",),
        }),
        ("Professional Information", {
            "fields": ("employee_id", "department", "designation", "phone"),
        }),
        ("Teaching Assignments", {
            "fields": ("subjects",),
        }),
        ("Salary Information", {
            "fields": ("salary_amount", "salary_status", "last_paid_date", "next_payment_date", "payment_notes"),
        }),
        ("System Info", {
            "fields": ("joined_date",),
            "classes": ("collapse",),
        }),
    )
    @admin.display(description="Teacher Name")
    def get_full_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        email = obj.user.email
        return format_html(
            '<strong>{}</strong><br><small style="color: #7f8c8d;">{}</small>',
            name, email
        )
    @admin.display(description="Salary Status")
    def salary_status_display(self, obj):
        color = "#2ecc71" if obj.salary_status == "paid" else "#e74c3c"
        label = "Paid" if obj.salary_status == "paid" else "Due"
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;">{}</span>',
            color, label
        )
    @admin.display(description="Salary")
    def salary_amount_display(self, obj):
        return format_html('<span style="color: #2ecc71;">₹ {:.0f}</span>', obj.salary_amount)
    @admin.display(description="Last Paid")
    def last_paid_date_display(self, obj):
        if obj.last_paid_date:
            return format_html('{}<br><small style="color: #7f8c8d;">{}</small>',
                obj.last_paid_date.strftime("%d %b %Y"),
                obj.last_paid_date.strftime("%b %Y")
            )
        return format_html('<span style="color: #e74c3c;">Never Paid</span>')
@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "get_teacher_name",
        "amount_display",
        "payment_date",
        "payment_method",
        "reference_number",
        "processed_by",
        "created_at",
    ]
    list_filter = ["payment_date", "payment_method", "created_at"]
    search_fields = [
        "teacher__user__first_name",
        "teacher__user__last_name",
        "teacher__employee_id",
        "reference_number",
    ]
    ordering = ["-payment_date"]
    raw_id_fields = ["teacher", "processed_by"]
    list_per_page = 30
    readonly_fields = ["created_at"]
    fieldsets = (
        ("Teacher Information", {
            "fields": ("teacher",),
        }),
        ("Payment Details", {
            "fields": ("amount", "payment_date", "payment_method", "reference_number"),
        }),
        ("Processing Information", {
            "fields": ("processed_by", "notes"),
        }),
        ("System Info", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )
    @admin.display(description="Teacher")
    def get_teacher_name(self, obj):
        name = obj.teacher.user.get_full_name()
        emp_id = obj.teacher.employee_id
        return format_html(
            '<strong>{}</strong><br><small style="color: #7f8c8d;">{}</small>',
            name, emp_id
        )
    @admin.display(description="Amount")
    def amount_display(self, obj):
        return format_html(
            '<span style="color: #2ecc71;">₹ {:.0f}</span>',
            obj.amount
        )
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "get_enrollment",
        "get_student_name",
        "subject",
        "semester",
        "attendance_display",
        "get_classes_info",
        "recorded_at",
    ]
    list_filter = ["semester", "subject__department", "recorded_at"]
    search_fields = [
        "student__enrollment_number",
        "student__user__first_name",
        "student__user__last_name",
        "subject__code",
        "subject__name",
    ]
    ordering = ["-recorded_at", "student__enrollment_number", "semester"]
    raw_id_fields = ["student"]
    readonly_fields = ["percentage", "recorded_at"]
    list_per_page = 30
    fieldsets = (
        ("Student & Subject", {
            "fields": ("student", "subject", "semester"),
        }),
        ("Attendance Data", {
            "fields": ("total_classes", "attended_classes", "percentage"),
        }),
        ("System Info", {
            "fields": ("recorded_at",),
            "classes": ("collapse",),
        }),
    )
    @admin.display(description="Enrollment")
    def get_enrollment(self, obj):
        return obj.student.enrollment_number
    @admin.display(description="Student")
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    @admin.display(description="Attendance")
    def attendance_display(self, obj):
        color = "#2ecc71" if obj.percentage >= 75 else "#f39c12" if obj.percentage >= 60 else "#e74c3c"
        icon = "✓" if obj.percentage >= 75 else "!" if obj.percentage >= 60 else "✗"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:.1f}%</span>',
            color, icon, obj.percentage
        )
    @admin.display(description="Classes")
    def get_classes_info(self, obj):
        return format_html(
            '<small>{} / {}</small>',
            obj.attended_classes, obj.total_classes
        )
