"""Permission decorators for the messaging system.
Provides role-based access control, restriction checking, and activity logging.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import UserRestriction, ActivityLog, Message, BroadcastRecipient
from .utils import can_send_message, can_view_message, get_user_restrictions
def require_not_restricted():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": "Please log in first."}, status=401)
                return redirect("login")
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                restrictions = get_user_restrictions(request.user)
                if restrictions.exists():
                    restriction = restrictions.first()
                    if not restriction.can_send_messages:
                        error_msg = f"You are {restriction.get_restriction_type_display().lower()} and cannot perform this action."
                        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                            return JsonResponse({"error": error_msg}, status=403)
                        django_messages.error(request, error_msg)
                        return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator
def require_teacher_only():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            if request.user.role != "teacher":
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Only teachers can access this."}, status=403
                    )
                django_messages.error(
                    request, "Only teachers can access this resource."
                )
                return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def require_admin_only():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            if request.user.role != "admin":
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": "Admin access required."}, status=403)
                django_messages.error(request, "Admin access required.")
                return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def require_teacher_for_department(department_param="department"):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            department = request.POST.get(department_param) or request.GET.get(
                department_param
            )
            if request.user.role == "admin":
                return view_func(request, *args, **kwargs)
            if department and request.user.role == "teacher":
                if not hasattr(request.user, "teacher_profile"):
                    django_messages.error(request, "Teacher profile not found.")
                    return redirect("messaging:inbox")
                if request.user.teacher_profile.department != department:
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {"error": "You can only broadcast to your department."},
                            status=403,
                        )
                    django_messages.error(
                        request, "You can only send broadcasts to your own department."
                    )
                    return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def require_teacher_or_admin():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            if request.user.role not in ["teacher", "admin"]:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Only teachers and admins can access this."},
                        status=403,
                    )
                django_messages.error(
                    request, "Only teachers and admins can access this resource."
                )
                return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def require_admin():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            if request.user.role != "admin":
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": "Admin access required."}, status=403)
                django_messages.error(request, "Admin access required.")
                return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def check_message_permission():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Authentication required."}, status=401
                    )
                return redirect("login")
            message_id = kwargs.get("message_id") or kwargs.get("pk")
            if not message_id and request.method == "POST":
                message_id = request.POST.get("message_id")
            if message_id:
                try:
                    message = Message.objects.get(id=message_id)
                    if not can_view_message(request.user, message):
                        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                            return JsonResponse(
                                {"error": "Permission denied."}, status=403
                            )
                        django_messages.error(
                            request, "You do not have permission to view this message."
                        )
                        return redirect("messaging:inbox")
                except Message.DoesNotExist:
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse({"error": "Message not found."}, status=404)
                    django_messages.error(request, "Message not found.")
                    return redirect("messaging:inbox")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
def log_activity(action_type="", include_metadata=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
            metadata = {}
            if include_metadata and request.method == "POST":
                excluded_fields = {"password", "token", "secret", "key"}
                metadata = {
                    k: v
                    for k, v in request.POST.items()
                    if k.lower() not in excluded_fields
                }
            response = view_func(request, *args, **kwargs)
            if request.user.is_authenticated and action_type:
                ActivityLog.objects.create(
                    user=request.user,
                    action_type=action_type,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata=metadata,
                )
            return response
        return wrapper
    return decorator
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
