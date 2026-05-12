"""API views for the student module.
Provides JSON endpoints for mobile apps and external integrations.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from students.models import Student, Marks, Subject, Teacher
from analytics.models import Prediction, PerformanceAnalytics
import json
@login_required
@require_http_methods(["GET"])
def api_student_profile(request):
    """Get student profile details.
    Returns:
        JSON response with student profile, CGPA, and alerts
    """
    try:
        student = request.user.student_profile
        cgpa = student.cgpa or student.calculate_cgpa()
        data = {
            "success": True,
            "student": {
                "id": student.id,
                "enrollment_number": student.enrollment_number,
                "name": request.user.get_full_name(),
                "email": request.user.email,
                "department": student.department,
                "semester": student.semester,
                "attendance": student.attendance,
                "cgpa": round(cgpa, 2),
                "enrolled_date": student.enrolled_date.isoformat(),
            },
            "grade": {
                "points": round(cgpa, 2),
                "letter": Student.grade_point_to_grade(cgpa)[0],
                "description": Student.grade_point_to_grade(cgpa)[1],
            },
        }
        try:
            pred = student.prediction
            data["prediction"] = {
                "risk_level": pred.risk_level,
                "predicted_score": pred.predicted_score,
                "predicted_cgpa": pred.predicted_cgpa,
                "performance_trend": pred.performance_trend,
            }
        except Prediction.DoesNotExist:
            pass
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Student profile not found"}, status=404
        )
@login_required
@require_http_methods(["GET"])
def api_student_marks(request):
    """Get student marks with optional semester filter.
    Query parameters:
        semester: Filter by specific semester (optional)
    Returns:
        JSON response with marks list and average
    """
    try:
        student = request.user.student_profile
        semester = request.GET.get("semester")
        if semester:
            try:
                semester_num = int(semester)
                semester_subjects = Subject.objects.filter(
                    department=student.department, semester=semester_num
                )
                marks_qs = student.marks.filter(subject__in=semester_subjects)
            except ValueError:
                return JsonResponse(
                    {"success": False, "error": "Invalid semester number"}, status=400
                )
        else:
            marks_qs = student.marks.all()
        marks_data = []
        for mark in marks_qs.select_related("subject"):
            marks_data.append(
                {
                    "subject_code": mark.subject.code,
                    "subject_name": mark.subject.name,
                    "score": mark.score,
                    "grade": mark.get_grade(),
                    "grade_point": mark.get_grade_point(),
                    "exam_type": mark.exam_type,
                    "credits": mark.subject.credits,
                }
            )
        average = marks_qs.aggregate(avg=Avg("score"))["avg"] or 0
        return JsonResponse(
            {
                "success": True,
                "semester": semester or "all",
                "marks": marks_data,
                "average": round(average, 2),
                "count": len(marks_data),
            }
        )
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Student profile not found"}, status=404
        )
@login_required
@require_http_methods(["GET"])
def api_student_performance(request):
    """Get student performance history and trends.
    Returns:
        JSON response with semester-wise performance data
    """
    try:
        student = request.user.student_profile
        history = student.performance_history.order_by("semester")
        history_data = []
        for record in history:
            history_data.append(
                {
                    "semester": record.semester,
                    "sgpa": record.sgpa,
                    "cgpa": record.cgpa,
                    "attendance": record.attendance,
                    "total_credits": record.total_credits,
                    "recorded_at": record.recorded_at.isoformat(),
                }
            )
        return JsonResponse(
            {
                "success": True,
                "history": history_data,
                "count": len(history_data),
            }
        )
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Student profile not found"}, status=404
        )
@login_required
@require_http_methods(["GET"])
def api_department_stats(request):
    """Get department-wise statistics (teachers only).
    Returns:
        JSON response with department statistics
    """
    if not request.user.is_staff:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )
    stats = PerformanceAnalytics.get_department_stats()
    stats_data = []
    for stat in stats:
        stats_data.append(
            {
                "department": stat["department"],
                "total_students": stat["total"],
                "avg_cgpa": round(stat["avg_cgpa"] or 0, 2),
                "avg_attendance": round(stat["avg_attendance"] or 0, 2),
            }
        )
    return JsonResponse(
        {
            "success": True,
            "stats": stats_data,
        }
    )
@login_required
@require_http_methods(["GET"])
def api_risk_distribution(request):
    """Get risk level distribution (teachers/admins only).
    Returns:
        JSON response with risk distribution
    """
    if not request.user.is_staff:
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )
    dist = PerformanceAnalytics.get_risk_distribution()
    risk_data = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }
    for record in dist:
        risk_data[record["risk_level"]] = record["count"]
    return JsonResponse(
        {
            "success": True,
            "distribution": risk_data,
            "total": sum(risk_data.values()),
        }
    )
