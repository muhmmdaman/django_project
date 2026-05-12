from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from .models import TimeSlot
from .forms import TimeSlotForm, TimetableFilterForm
from students.models import Subject, Student
@login_required
def timetable_view(request):
    user = request.user
    dept_filter = request.GET.get("department", "")
    semester_filter = request.GET.get("semester", "")
    if hasattr(user, "student_profile"):
        student = user.student_profile
        timeslots = (
            TimeSlot.objects.filter(
                department=student.department, semester=student.semester
            )
            .select_related("subject", "faculty")
            .order_by("day_of_week", "start_time")
        )
        user_type = "student"
        current_dept = student.department
        current_semester = student.semester
        can_manage = False
    elif user.is_staff or user.role == "teacher":
        if dept_filter and semester_filter:
            timeslots = TimeSlot.objects.filter(
                department=dept_filter, semester=semester_filter
            )
        elif dept_filter:
            timeslots = TimeSlot.objects.filter(department=dept_filter)
        elif semester_filter:
            timeslots = TimeSlot.objects.filter(semester=semester_filter)
        else:
            if hasattr(user, "teacher_profile"):
                teacher = user.teacher_profile
                timeslots = TimeSlot.objects.filter(department=teacher.department)
                dept_filter = teacher.department
            else:
                timeslots = TimeSlot.objects.all()
        timeslots = timeslots.select_related("subject", "faculty").order_by(
            "day_of_week", "start_time"
        )
        user_type = "teacher"
        current_dept = dept_filter
        current_semester = semester_filter
        can_manage = True
    else:
        django_messages.error(request, "You don't have access to timetable.")
        return redirect("core:dashboard")
    filter_form = TimetableFilterForm(
        initial={
            "department": dept_filter,
            "semester": semester_filter,
        }
    )
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    timetable_by_day = {}
    for day in days:
        timetable_by_day[day] = list(timeslots.filter(day_of_week=day))
    time_slots_set = set()
    for slot in timeslots:
        time_slots_set.add((slot.start_time, slot.end_time))
    time_slots_list = sorted(list(time_slots_set), key=lambda x: x[0])
    grid_data = {}
    for day in days:
        grid_data[day] = {}
        for time_slot in time_slots_list:
            matching = [
                s
                for s in timetable_by_day[day]
                if s.start_time == time_slot[0] and s.end_time == time_slot[1]
            ]
            grid_data[day][time_slot] = matching[0] if matching else None
    dept_choices = [
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
    context = {
        "timetable_by_day": timetable_by_day,
        "days": days,
        "day_labels": day_labels,
        "user_type": user_type,
        "timeslots": timeslots,
        "time_slots_list": time_slots_list,
        "grid_data": grid_data,
        "current_dept": current_dept,
        "current_semester": current_semester,
        "can_manage": can_manage,
        "filter_form": filter_form,
        "dept_choices": dept_choices,
        "semester_choices": range(1, 9),
    }
    return render(request, "timetable/timetable.html", context)
@login_required
def add_timeslot(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        django_messages.error(
            request, "You don't have permission to add timetable entries."
        )
        return redirect("timetable:timetable")
    if request.method == "POST":
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            timeslot = form.save()
            django_messages.success(
                request,
                f"Time slot for {timeslot.subject.name} on {timeslot.get_day_of_week_display()} added successfully!",
            )
            dept = timeslot.department
            sem = timeslot.semester
            return redirect(
                f"{request.build_absolute_uri('/timetable/')}?department={dept}&semester={sem}"
            )
    else:
        initial = {}
        if request.GET.get("department"):
            initial["department"] = request.GET.get("department")
        if request.GET.get("semester"):
            initial["semester"] = request.GET.get("semester")
        form = TimeSlotForm(initial=initial)
    context = {
        "form": form,
        "title": "Add Time Slot",
        "button_text": "Add Time Slot",
    }
    return render(request, "timetable/timeslot_form.html", context)
@login_required
def edit_timeslot(request, pk):
    if not (request.user.is_staff or request.user.role == "teacher"):
        django_messages.error(
            request, "You don't have permission to edit timetable entries."
        )
        return redirect("timetable:timetable")
    timeslot = get_object_or_404(TimeSlot, pk=pk)
    if request.method == "POST":
        form = TimeSlotForm(request.POST, instance=timeslot)
        if form.is_valid():
            timeslot = form.save()
            django_messages.success(request, "Time slot updated successfully!")
            return redirect("timetable:timetable")
    else:
        form = TimeSlotForm(instance=timeslot)
    context = {
        "form": form,
        "title": "Edit Time Slot",
        "button_text": "Update Time Slot",
        "timeslot": timeslot,
    }
    return render(request, "timetable/timeslot_form.html", context)
@login_required
def delete_timeslot(request, pk):
    if not (request.user.is_staff or request.user.role == "teacher"):
        django_messages.error(
            request, "You don't have permission to delete timetable entries."
        )
        return redirect("timetable:timetable")
    timeslot = get_object_or_404(TimeSlot, pk=pk)
    if request.method == "POST":
        subject_name = timeslot.subject.name
        day = timeslot.get_day_of_week_display()
        timeslot.delete()
        django_messages.success(
            request, f"Time slot for {subject_name} on {day} deleted successfully!"
        )
        return redirect("timetable:timetable")
    context = {
        "timeslot": timeslot,
    }
    return render(request, "timetable/timeslot_confirm_delete.html", context)
@login_required
def get_subjects_by_dept_semester(request):
    dept = request.GET.get("department", "")
    semester = request.GET.get("semester", "")
    subjects = Subject.objects.all()
    if dept:
        subjects = subjects.filter(department__in=[dept, "GEN"])
    if semester:
        subjects = subjects.filter(semester=int(semester))
    data = [
        {"id": s.id, "name": f"{s.code} - {s.name}", "is_lab": s.is_lab}
        for s in subjects.order_by("code")
    ]
    return JsonResponse({"subjects": data})
