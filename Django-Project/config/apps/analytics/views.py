from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Prediction, PerformanceAnalytics

@login_required
def analytics_dashboard(request):
    """Main analytics dashboard for all users"""
    user = request.user

    if user.role == 'admin':
        return admin_analytics(request)
    elif user.is_student:
        return student_analytics(request)
    elif user.is_teacher:
        return teacher_analytics(request)

    return render(request, 'analytics/dashboard.html')

@login_required
def admin_analytics(request):
    """Admin analytics view with department and system-wide statistics"""
    dept_stats = PerformanceAnalytics.get_department_stats()
    risk_distribution = PerformanceAnalytics.get_risk_distribution()
    top_performers = PerformanceAnalytics.get_top_performers(limit=5)
    most_improved = PerformanceAnalytics.get_most_improved(limit=5)
    low_performers = PerformanceAnalytics.get_consistently_low_performers(limit=10)

    context = {
        'dept_stats': dept_stats,
        'risk_distribution': risk_distribution,
        'top_performers': top_performers,
        'most_improved': most_improved,
        'low_performers': low_performers,
    }
    return render(request, 'analytics/admin_analytics.html', context)

@login_required
def student_analytics(request):
    """Student-specific analytics and performance prediction"""
    try:
        student = request.user.student_profile
        prediction = Prediction.objects.filter(student=student).first()
        alerts = PerformanceAnalytics.get_alerts(student)

        context = {
            'student': student,
            'prediction': prediction,
            'alerts': alerts,
        }
        return render(request, 'analytics/student_analytics.html', context)
    except Exception as e:
        context = {'error': str(e)}
        return render(request, 'analytics/error.html', context)

@login_required
def teacher_analytics(request):
    """Teacher analytics for their classes"""
    try:
        teacher = request.user.teacher_profile
        # Get department statistics for teacher's department
        dept_stats = PerformanceAnalytics.get_department_stats()
        dept_stats = [s for s in dept_stats if s['department'] == teacher.department]

        context = {
            'teacher': teacher,
            'dept_stats': dept_stats,
        }
        return render(request, 'analytics/teacher_analytics.html', context)
    except Exception as e:
        context = {'error': str(e)}
        return render(request, 'analytics/error.html', context)

@login_required
def performance_details(request):
    """Detailed performance analysis page"""
    if request.user.is_student:
        try:
            student = request.user.student_profile
            prediction = Prediction.objects.filter(student=student).first()
            context = {'prediction': prediction, 'student': student}
            return render(request, 'analytics/performance_details.html', context)
        except:
            pass
    return render(request, 'analytics/performance_details.html')

@login_required
def risk_analysis(request):
    """Risk level analysis page"""
    if request.user.role == 'admin':
        risk_distribution = PerformanceAnalytics.get_risk_distribution()
        low_performers = PerformanceAnalytics.get_consistently_low_performers(limit=20)
        context = {
            'risk_distribution': risk_distribution,
            'low_performers': low_performers,
        }
        return render(request, 'analytics/risk_analysis.html', context)
    return render(request, 'analytics/unauthorized.html')
