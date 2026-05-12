from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg, Count, Q
from students.models import Student, Marks, Subject
from analytics.models import Prediction, PerformanceAnalytics
@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return admin_dashboard(request)
    elif user.is_student:
        return student_dashboard(request)
    elif user.is_teacher:
        return teacher_dashboard(request)
    else:
        return student_dashboard(request)
def admin_dashboard(request):
    from messaging.models import Message, UserRestriction, ActivityLog
    from accounts.models import CustomUser
    from django.utils import timezone
    from datetime import timedelta
    total_users = CustomUser.objects.count()
    total_admins = CustomUser.objects.filter(role='admin').count()
    total_teachers = CustomUser.objects.filter(role='teacher').count()
    total_students = Student.objects.count()
    seven_days_ago = timezone.now() - timedelta(days=7)
    active_users = CustomUser.objects.filter(last_activity__gte=seven_days_ago).count()
    total_messages = Message.objects.count()
    messages_today = Message.objects.filter(timestamp__date=timezone.now().date()).count()
    broadcasts = Message.objects.filter(message_type='broadcast').count()
    private_messages = Message.objects.filter(message_type='private').count()
    banned_users = UserRestriction.objects.filter(restriction_type='banned', is_active=True).count()
    muted_users = UserRestriction.objects.filter(restriction_type='muted', is_active=True).count()
    recent_activity = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]
    dept_stats = []
    for dept_code, dept_name in Student.DEPARTMENT_CHOICES:
        dept_students = Student.objects.filter(department=dept_code)
        dept_teachers = CustomUser.objects.filter(role='teacher', teacher_profile__department=dept_code)
        dept_stats.append({
            'code': dept_code,
            'name': dept_name,
            'student_count': dept_students.count(),
            'teacher_count': dept_teachers.count(),
        })
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'active_users': active_users,
        'total_messages': total_messages,
        'messages_today': messages_today,
        'broadcasts': broadcasts,
        'private_messages': private_messages,
        'banned_users': banned_users,
        'muted_users': muted_users,
        'recent_activity': recent_activity,
        'dept_stats': dept_stats,
    }
    return render(request, 'core/admin_dashboard.html', context)
def student_dashboard(request):
    user = request.user
    try:
        student = user.student_profile
        selected_semester = request.GET.get("semester", "")
        if selected_semester and selected_semester != "all":
            semester_num = int(selected_semester)
            semester_subjects = Subject.objects.filter(
                Q(department=student.department) | Q(department="GEN"),
                semester=semester_num,
            )
            marks = (
                Marks.objects.filter(student=student, subject__in=semester_subjects)
                .select_related("subject")
                .order_by("subject__is_lab", "subject__code")
            )
            gpa_value = student.calculate_sgpa(semester_num)
            gpa_label = "SGPA"
            attendance_value = student.get_semester_attendance(semester_num)
            selected_semester = semester_num
        else:
            marks = (
                Marks.objects.filter(student=student)
                .select_related("subject")
                .order_by("subject__semester", "subject__code")
            )
            gpa_value = student.cgpa or student.calculate_cgpa()
            gpa_label = "CGPA"
            attendance_value = student.attendance
            selected_semester = "all"
        average = student.get_average_marks()
        semester_average = marks.aggregate(avg=Avg("score"))["avg"] or 0
        grade, grade_desc = student.grade_point_to_grade(gpa_value)
        classification, class_color = student.get_grade_classification()
        marks_list = list(marks.values_list("score", flat=True))
        highest_score = max(marks_list) if marks_list else 0
        lowest_score = min(marks_list) if marks_list else 0
        passed_count = sum(1 for s in marks_list if s >= 50)
        failed_count = len(marks_list) - passed_count
        history = list(
            student.performance_history.order_by("semester").values(
                "semester", "sgpa", "cgpa", "attendance"
            )
        )
        try:
            prediction = student.prediction
        except Prediction.DoesNotExist:
            prediction = None
        alerts = PerformanceAnalytics.get_alerts(student)
        weak_subjects = student.get_weakest_subjects()
        strong_subjects = student.get_strongest_subjects()
        available_semesters = range(1, student.semester + 1)
        context = {
            "student": student,
            "marks": marks,
            "average": average,
            "semester_average": semester_average,
            "cgpa": gpa_value,
            "gpa_label": gpa_label,
            "grade": grade,
            "grade_desc": grade_desc,
            "classification": classification,
            "class_color": class_color,
            "prediction": prediction,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "history": history,
            "alerts": alerts,
            "weak_subjects": weak_subjects,
            "strong_subjects": strong_subjects,
            "selected_semester": selected_semester,
            "available_semesters": available_semesters,
            "attendance": attendance_value,
        }
        return render(request, "core/student_dashboard.html", context)
    except Student.DoesNotExist:
        return render(
            request,
            "core/student_dashboard.html",
            {
                "error": "Student profile not found. Please contact administrator.",
            },
        )
def teacher_dashboard(request):
    students = Student.objects.select_related("user").prefetch_related(
        "marks", "prediction"
    )
    selected_department = request.GET.get("department", "")
    selected_semester = request.GET.get("semester", "")
    if selected_department:
        students = students.filter(department=selected_department)
    if selected_semester:
        students = students.filter(semester=int(selected_semester))
    dept_stats = []
    for dept_code, dept_name in Student.DEPARTMENT_CHOICES:
        dept_students = students.filter(department=dept_code)
        if dept_students.exists():
            if selected_semester:
                marks = Marks.objects.filter(
                    student__in=dept_students, subject__semester=int(selected_semester)
                )
            else:
                marks = Marks.objects.filter(student__in=dept_students)
            avg_marks = marks.aggregate(avg=Avg("score"))["avg"] or 0
            avg_attendance = dept_students.aggregate(avg=Avg("attendance"))["avg"] or 0
            avg_cgpa = (
                dept_students.filter(cgpa__isnull=False).aggregate(avg=Avg("cgpa"))[
                    "avg"
                ]
                or 0
            )
            risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for s in dept_students:
                try:
                    risk_counts[s.prediction.risk_level] += 1
                except (Prediction.DoesNotExist, AttributeError, KeyError):
                    pass
            dept_stats.append(
                {
                    "code": dept_code,
                    "name": dept_name,
                    "student_count": dept_students.count(),
                    "avg_marks": round(avg_marks, 1),
                    "avg_attendance": round(avg_attendance, 1),
                    "avg_cgpa": round(avg_cgpa, 2),
                    "risk_counts": risk_counts,
                }
            )
    total_students = students.count()
    if selected_semester:
        overall_marks = Marks.objects.filter(
            student__in=students, subject__semester=int(selected_semester)
        )
    else:
        overall_marks = Marks.objects.filter(student__in=students)
    overall_avg = overall_marks.aggregate(avg=Avg("score"))["avg"] or 0
    overall_cgpa = (
        students.filter(cgpa__isnull=False).aggregate(avg=Avg("cgpa"))["avg"] or 0
    )
    risk_dist = dict(
        Prediction.objects.filter(student__in=students)
        .values("risk_level")
        .annotate(count=Count("id"))
        .values_list("risk_level", "count")
    )
    low_risk_count = risk_dist.get("low", 0)
    medium_risk_count = risk_dist.get("medium", 0)
    high_risk_count = risk_dist.get("high", 0)
    critical_risk_count = risk_dist.get("critical", 0)
    attendance_risk_count = students.filter(attendance__lt=75).count()
    critical_attendance = students.filter(attendance__lt=60).count()
    at_risk_students = students.filter(
        prediction__risk_level__in=["high", "critical"]
    ).order_by("prediction__predicted_score")[:10]
    top_performers = PerformanceAnalytics.get_top_performers(limit=5)
    most_improved = PerformanceAnalytics.get_most_improved(limit=5)
    context = {
        "students": students.order_by("-enrolled_date")[:12],
        "dept_stats": dept_stats,
        "total_students": total_students,
        "overall_avg": round(overall_avg, 1),
        "overall_cgpa": round(overall_cgpa, 2),
        "at_risk_students": at_risk_students,
        "top_performers": top_performers,
        "most_improved": most_improved,
        "low_risk_count": low_risk_count,
        "medium_risk_count": medium_risk_count,
        "high_risk_count": high_risk_count,
        "critical_risk_count": critical_risk_count,
        "attendance_risk_count": attendance_risk_count,
        "critical_attendance": critical_attendance,
        "department_choices": Student.DEPARTMENT_CHOICES,
        "semester_choices": [(i, f"Semester {i}") for i in range(1, 9)],
        "selected_department": selected_department,
        "selected_semester": selected_semester,
    }
    return render(request, "core/teacher_dashboard.html", context)
def not_found_view(request, exception=None):
    return render(request, "404.html", status=404)
def forbidden_view(request, exception=None):
    return render(request, "403.html", status=403)
def server_error_view(request, exception=None):
    return render(request, "500.html", status=500)
