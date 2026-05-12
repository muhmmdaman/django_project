from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from students.models import Student
from .models import Complaint
from .forms import ComplaintForm, ResolutionForm
@login_required
def complaints_list(request):
    user = request.user
    if user.is_student:
        complaints = Complaint.objects.filter(student__user=user).order_by(
            "-created_at"
        )
    else:
        complaints = Complaint.objects.all().order_by("-created_at")
    status_filter = request.GET.get("status")
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    context = {
        "complaints": complaints,
        "selected_status": status_filter,
    }
    return render(request, "complaints/complaints_list.html", context)
@login_required
def submit_complaint(request):
    if not hasattr(request.user, "student_profile"):
        django_messages.error(request, "Only students can submit complaints.")
        return redirect("core:dashboard")
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user.student_profile
            complaint.save()
            django_messages.success(request, "Complaint submitted successfully!")
            return redirect("complaints:complaints_list")
    else:
        form = ComplaintForm()
    context = {"form": form}
    return render(request, "complaints/submit_complaint.html", context)
@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    user = request.user
    is_owner = (
        user.student_profile == complaint.student
        if hasattr(user, "student_profile")
        else False
    )
    is_admin = user.is_staff or user.is_superuser
    if not (is_owner or is_admin):
        django_messages.error(
            request, "You don't have permission to view this complaint."
        )
        return redirect("complaints:complaints_list")
    if request.method == "POST" and is_admin:
        form = ResolutionForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            django_messages.success(request, "Complaint updated!")
            return redirect("complaints:complaint_detail", pk=pk)
    else:
        form = ResolutionForm(instance=complaint) if is_admin else None
    context = {
        "complaint": complaint,
        "form": form,
        "is_admin": is_admin,
    }
    return render(request, "complaints/complaint_detail.html", context)
