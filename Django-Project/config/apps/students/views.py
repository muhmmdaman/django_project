import csv
import io
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from accounts.models import CustomUser
from analytics.models import Prediction, PerformanceAnalytics
from .models import (
    Student,
    Marks,
    Subject,
    PerformanceHistory,
    Teacher,
    TeacherSubjectAssignmentDocument,
    SalaryPayment,
)
from .forms import (
    StudentForm,
    MarksForm,
    StudentCSVUploadForm,
    MarksCSVUploadForm,
    TeacherSubjectAssignmentDocumentForm,
    TeacherSubjectAssignmentApprovalForm,
    TeacherSalaryStatusForm,
    SalaryPaymentForm,
)
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 15
    def get_queryset(self):
        queryset = Student.objects.select_related("user").prefetch_related(
            "marks", "prediction"
        )
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(enrollment_number__icontains=search_query)
                | Q(user__email__icontains=search_query)
            )
        dept_filter = self.request.GET.get("department")
        if dept_filter:
            queryset = queryset.filter(department=dept_filter)
        sem_filter = self.request.GET.get("semester")
        if sem_filter:
            queryset = queryset.filter(semester=int(sem_filter))
        risk_filter = self.request.GET.get("risk_level")
        if risk_filter:
            queryset = queryset.filter(prediction__risk_level=risk_filter)
        return queryset.order_by("-enrolled_date")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["department_choices"] = Student.DEPARTMENT_CHOICES
        context["semester_choices"] = [(i, f"Semester {i}") for i in range(1, 9)]
        context["risk_choices"] = Prediction.RISK_LEVELS
        context["selected_department"] = self.request.GET.get("department", "")
        context["selected_semester"] = self.request.GET.get("semester", "")
        context["selected_risk"] = self.request.GET.get("risk_level", "")
        context["search_query"] = self.request.GET.get("search", "")
        return context
@login_required
def add_student(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        messages.error(request, "Only teachers and administrators can add students.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = f"{first_name.lower()}.{last_name.lower()}"
            base_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = CustomUser.objects.create_user(
                username=username,
                email=form.cleaned_data["email"],
                first_name=first_name,
                last_name=last_name,
                password="student123",
                role="student",
            )
            student = form.save(commit=False)
            student.user = user
            student.enrollment_number = form.cleaned_data["enrollment_number"]
            student.save()
            Prediction.generate_prediction(student)
            messages.success(
                request,
                f"Student '{user.get_full_name()}' ({student.enrollment_number}) created! Default password: student123",
            )
            return redirect("students:student_list")
    else:
        form = StudentForm()
    return render(request, "students/add_student.html", {"form": form})
@login_required
def add_marks(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        messages.error(request, "Only teachers and administrators can add marks.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = MarksForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data["student"]
            subject = form.cleaned_data["subject"]
            exam_type = form.cleaned_data.get("exam_type", "END")
            marks, created = Marks.objects.update_or_create(
                student=student,
                subject=subject,
                exam_type=exam_type,
                defaults={"score": form.cleaned_data["score"]},
            )
            if created:
                messages.success(
                    request,
                    f"Marks added for {student.enrollment_number} in {subject.code}.",
                )
            else:
                messages.info(
                    request,
                    f"Marks updated for {student.enrollment_number} in {subject.code}.",
                )
            return redirect("students:add_marks")
    else:
        form = MarksForm()
    return render(request, "students/add_marks.html", {"form": form})
@login_required
def student_detail(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("user").prefetch_related(
            "marks__subject", "performance_history"
        ),
        pk=pk,
    )
    selected_semester = request.GET.get("semester", "")
    if selected_semester and selected_semester != "all":
        semester_subjects = Subject.objects.filter(
            Q(department=student.department) | Q(department="GEN"),
            semester=int(selected_semester),
        )
        marks = (
            student.marks.filter(subject__in=semester_subjects)
            .select_related("subject")
            .order_by("subject__code")
        )
        average = marks.aggregate(avg=Avg("score"))["avg"] or 0
        selected_semester = int(selected_semester)
    else:
        marks = (
            student.marks.all()
            .select_related("subject")
            .order_by("subject__semester", "subject__code")
        )
        average = student.get_average_marks()
        selected_semester = "all"
    cgpa = student.cgpa or student.calculate_cgpa()
    grade, grade_desc = student.grade_point_to_grade(cgpa)
    classification, class_color = student.get_grade_classification()
    history = student.performance_history.order_by("semester")
    try:
        prediction = student.prediction
    except Prediction.DoesNotExist:
        prediction = None
    alerts = PerformanceAnalytics.get_alerts(student)
    available_semesters = range(1, student.semester + 1)
    context = {
        "student": student,
        "marks": marks,
        "average": average,
        "cgpa": cgpa,
        "grade": grade,
        "grade_desc": grade_desc,
        "classification": classification,
        "class_color": class_color,
        "prediction": prediction,
        "history": list(history.values("semester", "sgpa", "cgpa", "attendance")),
        "alerts": alerts,
        "weak_subjects": student.get_weakest_subjects(),
        "strong_subjects": student.get_strongest_subjects(),
        "selected_semester": selected_semester,
        "available_semesters": available_semesters,
    }
    return render(request, "students/student_detail.html", context)
@login_required
def upload_students_csv(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        messages.error(request, "Only teachers and administrators can upload students.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = StudentCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            decoded = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))
            created_count = 0
            errors = []
            for row_num, row in enumerate(reader, start=2):
                try:
                    required = [
                        "first_name",
                        "last_name",
                        "email",
                        "enrollment_number",
                        "department",
                    ]
                    for field in required:
                        if not row.get(field):
                            raise ValueError(f"Missing {field}")
                    if Student.objects.filter(
                        enrollment_number=row["enrollment_number"]
                    ).exists():
                        raise ValueError(
                            f"Enrollment {row['enrollment_number']} already exists"
                        )
                    username = f"{row['first_name'].lower()}.{row['last_name'].lower()}"
                    base = username
                    counter = 1
                    while CustomUser.objects.filter(username=username).exists():
                        username = f"{base}{counter}"
                        counter += 1
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=row["email"],
                        first_name=row["first_name"],
                        last_name=row["last_name"],
                        password="student123",
                        role="student",
                    )
                    Student.objects.create(
                        user=user,
                        enrollment_number=row["enrollment_number"],
                        department=row["department"].upper(),
                        semester=int(row.get("semester", 1)),
                        attendance=float(row.get("attendance", 100)),
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            if created_count:
                messages.success(
                    request, f"Successfully created {created_count} students."
                )
            if errors:
                messages.warning(request, f"Errors: {'; '.join(errors[:5])}")
            return redirect("students:student_list")
    else:
        form = StudentCSVUploadForm()
    context = {
        "form": form,
        "title": "Upload Students CSV",
        "sample_headers": "first_name,last_name,email,enrollment_number,department,semester,attendance",
    }
    return render(request, "students/csv_upload.html", context)
@login_required
def upload_marks_csv(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        messages.error(request, "Only teachers and administrators can upload marks.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = MarksCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            decoded = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))
            created_count = 0
            updated_count = 0
            errors = []
            for row_num, row in enumerate(reader, start=2):
                try:
                    enrollment = row.get("enrollment_number")
                    subject_code = row.get("subject_code")
                    score = float(row.get("score", 0))
                    exam_type = row.get("exam_type", "END")
                    if not enrollment or not subject_code:
                        raise ValueError("Missing enrollment_number or subject_code")
                    if score < 0 or score > 100:
                        raise ValueError(f"Invalid score: {score}")
                    student = Student.objects.get(enrollment_number=enrollment)
                    subject = Subject.objects.get(code=subject_code)
                    _, created = Marks.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_type=exam_type,
                        defaults={"score": score},
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    Prediction.generate_prediction(student)
                except Student.DoesNotExist:
                    errors.append(f"Row {row_num}: Student {enrollment} not found")
                except Subject.DoesNotExist:
                    errors.append(f"Row {row_num}: Subject {subject_code} not found")
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            if created_count or updated_count:
                messages.success(
                    request, f"Created {created_count}, updated {updated_count} marks."
                )
            if errors:
                messages.warning(request, f"Errors: {'; '.join(errors[:5])}")
            return redirect("students:student_list")
    else:
        form = MarksCSVUploadForm()
    context = {
        "form": form,
        "title": "Upload Marks CSV",
        "sample_headers": "enrollment_number,subject_code,score,exam_type",
    }
    return render(request, "students/csv_upload.html", context)
@login_required
def download_report(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("user").prefetch_related("marks__subject"),
        pk=pk,
    )
    marks = student.marks.all().select_related("subject")
    average = student.get_average_marks()
    cgpa = student.cgpa or student.calculate_cgpa()
    try:
        prediction = student.prediction
    except Prediction.DoesNotExist:
        prediction = None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f77b4")
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor("#1f77b4")
    )
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6,
    )
    story = []
    story.append(Paragraph("ACADEMIC INTELLIGENCE SYSTEM", title_style))
    story.append(Paragraph("Student Performance Report", styles["Heading3"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            normal_style,
        )
    )
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("STUDENT INFORMATION", section_style))
    grade, grade_desc = student.grade_point_to_grade(cgpa)
    classification, _ = student.get_grade_classification()
    info_data = [
        ["Name", student.user.get_full_name()],
        ["Enrollment No.", student.enrollment_number],
        ["Email", student.user.email],
        ["Department", student.get_class_name_display()],
        ["Semester", str(student.semester)],
        ["Attendance", f"{student.attendance:.1f}%"],
        ["CGPA", f"{cgpa:.2f} ({grade} - {grade_desc})"],
        ["Classification", classification],
    ]
    info_table = Table(info_data, colWidths=[1.8 * inch, 4.5 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f4f8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("SUBJECT-WISE MARKS & GRADES", section_style))
    if marks.exists():
        marks_data = [["Subject", "Code", "Score", "Grade", "Grade Point", "Credits"]]
        total_credits = 0
        total_gp = 0
        for mark in marks:
            gp = student.score_to_grade_point(mark.score)
            g, _ = student.grade_point_to_grade(gp)
            credits = mark.subject.credits
            total_credits += credits
            total_gp += gp * credits
            marks_data.append(
                [
                    mark.subject.name[:25],
                    mark.subject.code,
                    f"{mark.score:.1f}",
                    g,
                    f"{gp:.1f}",
                    str(credits),
                ]
            )
        marks_data.append(["", "", "", "", "", ""])
        marks_data.append(
            [
                "TOTAL / AVERAGE",
                "",
                f"{average:.1f}",
                "",
                f"{cgpa:.2f}",
                str(total_credits),
            ]
        )
        marks_table = Table(
            marks_data,
            colWidths=[
                2.2 * inch,
                0.8 * inch,
                0.8 * inch,
                0.7 * inch,
                0.9 * inch,
                0.7 * inch,
            ],
        )
        marks_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f4f8")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )
        story.append(marks_table)
    story.append(Spacer(1, 0.15 * inch))
    if prediction:
        story.append(Paragraph("AI PREDICTION & RISK ANALYSIS", section_style))
        risk_colors = {
            "low": colors.HexColor("#2ecc71"),
            "medium": colors.HexColor("#f39c12"),
            "high": colors.HexColor("#e74c3c"),
            "critical": colors.HexColor("#c0392b")
        }
        pred_data = [
            ["Predicted Score", f"{prediction.predicted_score:.1f}%"],
            ["Predicted CGPA", f"{prediction.predicted_cgpa:.2f}"],
            ["Risk Level", prediction.get_risk_level_display()],
            ["Performance Trend", prediction.get_performance_trend_display()],
            [
                "Attendance Risk",
                "Yes - Below 75%" if prediction.attendance_risk else "No",
            ],
        ]
        pred_table = Table(pred_data, colWidths=[1.8 * inch, 4.5 * inch])
        pred_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f4f8")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    (
                        "TEXTCOLOR",
                        (1, 2),
                        (1, 2),
                        risk_colors.get(prediction.risk_level, colors.gray),
                    ),
                    ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
                ]
            )
        )
        story.append(pred_table)
        story.append(Spacer(1, 0.15 * inch))
        if prediction.weak_subjects:
            story.append(Paragraph("WEAK SUBJECTS (Need Improvement)", section_style))
            for ws in prediction.weak_subjects[:3]:
                story.append(
                    Paragraph(
                        f"• {ws['name']} ({ws['code']}): {ws['score']:.0f}%",
                        normal_style,
                    )
                )
            story.append(Spacer(1, 0.1 * inch))
        if prediction.suggestions:
            story.append(Paragraph("RECOMMENDATIONS", section_style))
            for line in prediction.suggestions.split("\n"):
                if line.strip():
                    prefix = (
                        "▶"
                        if line.startswith(("CRITICAL", "URGENT", "ACTION"))
                        else "•"
                    )
                    story.append(Paragraph(f"{prefix} {line}", normal_style))
    story.append(Spacer(1, 0.3 * inch))
    footer_style = ParagraphStyle(
        "Footer", fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#7f8c8d")
    )
    story.append(Paragraph("─" * 60, footer_style))
    story.append(
        Paragraph(
            "Academic Intelligence System - Confidential Student Report", footer_style
        )
    )
    story.append(Paragraph("Contact administration for any queries.", footer_style))
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    filename = (
        f"report_{student.enrollment_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
@login_required
def teacher_upload_subject_document(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == "POST":
        form = TeacherSubjectAssignmentDocumentForm(
            request.POST, request.FILES, teacher=teacher
        )
        if form.is_valid():
            document = form.save(commit=False)
            document.teacher = teacher
            document.save()
            form.save_m2m()
            messages.success(
                request,
                f"Document '{document.document_name}' uploaded successfully. Awaiting admin approval.",
            )
            return redirect("students:teacher_documents_list")
    else:
        form = TeacherSubjectAssignmentDocumentForm(teacher=teacher)
    context = {
        "form": form,
        "page_title": "Upload Subject Assignment Document",
    }
    return render(request, "students/teacher_upload_document.html", context)
@login_required
def teacher_documents_list(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    documents = TeacherSubjectAssignmentDocument.objects.filter(
        teacher=teacher
    ).prefetch_related("subjects")
    status_filter = request.GET.get("status")
    if status_filter:
        documents = documents.filter(status=status_filter)
    context = {
        "documents": documents,
        "page_title": "My Subject Assignment Documents",
        "status_filter": status_filter,
    }
    return render(request, "students/teacher_documents_list.html", context)
@login_required
def admin_document_approval(request):
    from messaging.decorators import require_admin
    if request.user.role != "admin":
        return redirect("core:dashboard")
    pending_docs = TeacherSubjectAssignmentDocument.objects.filter(
        status="pending"
    ).select_related("teacher__user")
    status_filter = request.GET.get("status", "pending")
    if status_filter:
        documents = (
            TeacherSubjectAssignmentDocument.objects.filter(status=status_filter)
            .select_related("teacher__user")
            .order_by("-uploaded_at")
        )
    else:
        documents = TeacherSubjectAssignmentDocument.objects.select_related(
            "teacher__user"
        ).order_by("-uploaded_at")
    context = {
        "pending_count": pending_docs.count(),
        "documents": documents,
        "status_filter": status_filter,
        "page_title": "Document Approval Management",
    }
    return render(request, "students/admin_document_approval.html", context)
@login_required
def document_approve_reject(request, document_id):
    if request.user.role != "admin":
        return redirect("core:dashboard")
    document = get_object_or_404(TeacherSubjectAssignmentDocument, id=document_id)
    if request.method == "POST":
        form = TeacherSubjectAssignmentApprovalForm(request.POST, instance=document)
        if form.is_valid():
            status = form.cleaned_data["status"]
            notes = form.cleaned_data["approval_notes"]
            if status == "approved":
                document.approve(approved_by=request.user, notes=notes)
                messages.success(
                    request,
                    f"Document approved. {document.subjects.count()} subjects assigned to {document.teacher.user.get_full_name()}",
                )
            else:
                document.reject(approved_by=request.user, reason=notes)
                messages.warning(request, "Document rejected.")
            return redirect("students:admin_document_approval")
    else:
        form = TeacherSubjectAssignmentApprovalForm(instance=document)
    context = {
        "document": document,
        "form": form,
        "page_title": "Approve/Reject Document",
    }
    return render(request, "students/document_approve_reject.html", context)
@login_required
def teacher_salary_list(request):
    if request.user.role != "admin":
        messages.error(request, "Only administrators can access this page.")
        return redirect("core:dashboard")
    teachers = Teacher.objects.select_related("user").prefetch_related("salary_payments")
    dept_filter = request.GET.get("department")
    if dept_filter:
        teachers = teachers.filter(department=dept_filter)
    status_filter = request.GET.get("salary_status")
    if status_filter:
        teachers = teachers.filter(salary_status=status_filter)
    teachers = teachers.order_by("department", "user__first_name")
    context = {
        "teachers": teachers,
        "department_choices": Teacher.DEPARTMENT_CHOICES,
        "salary_status_choices": Teacher.SALARY_STATUS_CHOICES,
        "selected_department": dept_filter or "",
        "selected_status": status_filter or "",
        "page_title": "Teacher Salary Management",
    }
    return render(request, "students/teacher_salary_list.html", context)
@login_required
def edit_teacher_salary(request, teacher_id):
    if request.user.role != "admin":
        messages.error(request, "Only administrators can access this page.")
        return redirect("core:dashboard")
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = TeacherSalaryStatusForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Salary information for {teacher.user.get_full_name()} updated successfully.",
            )
            return redirect("students:teacher_salary_list")
    else:
        form = TeacherSalaryStatusForm(instance=teacher)
    context = {
        "form": form,
        "teacher": teacher,
        "page_title": f"Edit Salary - {teacher.user.get_full_name()}",
    }
    return render(request, "students/edit_teacher_salary.html", context)
@login_required
def add_salary_payment(request, teacher_id):
    if request.user.role != "admin":
        messages.error(request, "Only administrators can access this page.")
        return redirect("core:dashboard")
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = SalaryPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.teacher = teacher
            payment.processed_by = request.user
            payment.save()
            teacher.salary_status = "paid"
            teacher.last_paid_date = payment.payment_date
            teacher.save(update_fields=["salary_status", "last_paid_date"])
            messages.success(
                request,
                f"Salary payment of ₹{payment.amount} recorded for {teacher.user.get_full_name()}.",
            )
            return redirect("students:teacher_salary_detail", teacher_id=teacher_id)
    else:
        form = SalaryPaymentForm()
    context = {
        "form": form,
        "teacher": teacher,
        "page_title": f"Add Salary Payment - {teacher.user.get_full_name()}",
    }
    return render(request, "students/add_salary_payment.html", context)
@login_required
def teacher_salary_detail(request, teacher_id):
    if request.user.role != "admin":
        messages.error(request, "Only administrators can access this page.")
        return redirect("core:dashboard")
    teacher = get_object_or_404(
        Teacher.objects.select_related("user").prefetch_related("salary_payments"),
        id=teacher_id,
    )
    salary_payments = teacher.salary_payments.all().order_by("-payment_date")
    total_paid = sum(p.amount for p in salary_payments)
    last_payment = salary_payments.first() if salary_payments.exists() else None
    context = {
        "teacher": teacher,
        "salary_payments": salary_payments,
        "total_paid": total_paid,
        "last_payment": last_payment,
        "page_title": f"Salary Details - {teacher.user.get_full_name()}",
    }
    return render(request, "students/teacher_salary_detail.html", context)
