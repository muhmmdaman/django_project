"""Messaging views for the academic system.
Handles private messages, broadcasts, admin controls, and activity logging.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q, Count, F, Value
from django.db.models.functions import Coalesce, TruncDate
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from datetime import timedelta
from accounts.models import CustomUser
from students.models import Student
from .models import (
    Message,
    ActivityLog,
    UserRestriction,
    BroadcastRecipient,
    MessageRecipientGroup,
)
from .forms import (
    MessageForm,
    BroadcastMessageForm,
    ReplyForm,
    BroadcastForm,
    DepartmentBroadcastForm,
    GlobalBroadcastForm,
    AdminUserActionForm,
    MessageFilterForm,
    TeacherFilterForm,
    TeacherCreationForm,
    TeacherUpdateForm,
    SalaryPaymentForm,
    TeacherSalaryStatusForm,
    QuickSalaryPaymentForm,
)
from .decorators import (
    require_not_restricted,
    require_teacher_or_admin,
    require_admin,
    require_teacher_only,
    require_admin_only,
    require_teacher_for_department,
    check_message_permission,
    log_activity,
)
from .utils import (
    can_send_message,
    can_view_message,
    get_user_restrictions,
    log_activity as log_activity_util,
    get_client_ip,
)


@login_required
def inbox(request):
    user = request.user
    view_type = request.GET.get("view", "all")
    semester = request.GET.get("semester")
    unread_count = Message.objects.filter(
        receiver=user, is_read=False, message_type="private", is_deleted=False
    ).count()
    received_messages = (
        Message.objects.filter(receiver=user, message_type="private", is_deleted=False)
        .select_related("sender")
        .order_by("-timestamp")
    )
    broadcasts = Message.objects.filter(
        message_type="broadcast", is_deleted=False
    ).select_related("sender")
    if hasattr(user, "student"):
        broadcasts = broadcasts.filter(
            Q(department__isnull=True) | Q(department=user.student.department)
        )
    else:
        broadcasts = broadcasts.filter(department__isnull=True)
    broadcasts = broadcasts.order_by("-timestamp")
    if view_type == "private":
        all_messages = list(received_messages[:50])
    elif view_type == "broadcast":
        all_messages = list(broadcasts[:50])
    else:
        all_messages = sorted(
            list(received_messages[:30]) + list(broadcasts[:30]),
            key=lambda x: x.timestamp,
            reverse=True,
        )[:50]
    Message.objects.filter(receiver=user, is_read=False, message_type="private").update(
        is_read=True, read_at=timezone.now()
    )
    BroadcastRecipient.objects.filter(recipient=user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    context = {
        "unread_count": unread_count,
        "all_messages": all_messages,
        "received_messages": received_messages[:50],
        "broadcasts": broadcasts[:50],
        "view_type": view_type,
    }
    return render(request, "messaging/inbox.html", context)


@login_required
def sent_messages(request):
    user = request.user
    messages_sent = (
        Message.objects.filter(sender=user, is_deleted=False)
        .select_related("receiver")
        .order_by("-timestamp")[:50]
    )
    context = {"messages": messages_sent}
    return render(request, "messaging/sent.html", context)


@login_required
@require_not_restricted()
@log_activity(action_type="message_sent", include_metadata=True)
def send_message(request):
    can_send, reason = can_send_message(request.user)
    if not can_send:
        django_messages.error(request, reason)
        return redirect("messaging:inbox")
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.message_type = "private"
            message.receiver_type = "individual"
            message.created_via = "ui"
            receiver = form.cleaned_data.get("receiver")
            message.save()
            log_activity_util(
                user=request.user,
                action_type="message_sent",
                target_user=receiver,
                message=message,
                ip_address=get_client_ip(request),
                metadata={"receiver": receiver.username},
            )
            django_messages.success(request, "Message sent successfully!")
            return redirect("messaging:inbox")
    else:
        form = MessageForm()
        form.fields["receiver"].queryset = CustomUser.objects.exclude(
            id=request.user.id
        ).filter(Q(role="student") | Q(role="teacher"))
    context = {"form": form}
    return render(request, "messaging/send_message.html", context)


@login_required
@check_message_permission()
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if not can_view_message(request.user, message):
        django_messages.error(
            request, "You don't have permission to view this message."
        )
        return redirect("messaging:inbox")
    if request.user == message.receiver and not message.is_read:
        message.mark_as_read()
    if message.message_type == "broadcast":
        BroadcastRecipient.objects.filter(
            message=message, recipient=request.user
        ).update(is_read=True, read_at=timezone.now())
    replies = message.replies.select_related("sender").order_by("timestamp")
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.receiver = (
                message.sender if request.user == message.receiver else message.receiver
            )
            reply.message_type = "private"
            reply.parent_message = message
            reply.save()
            log_activity_util(
                user=request.user,
                action_type="message_sent",
                target_user=reply.receiver,
                message=reply,
                ip_address=get_client_ip(request),
            )
            django_messages.success(request, "Reply sent!")
            return redirect("messaging:message_detail", pk=pk)
    else:
        form = ReplyForm()
    context = {
        "message": message,
        "replies": replies,
        "form": form,
    }
    return render(request, "messaging/message_detail.html", context)


@login_required
@require_teacher_or_admin()
@require_not_restricted()
@log_activity(action_type="broadcast_sent", include_metadata=True)
def send_broadcast(request):
    if request.method == "POST":
        form = BroadcastMessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            department = form.cleaned_data.get("department", "")
            message = Message.objects.create(
                sender=request.user,
                content=content,
                message_type="broadcast",
                department=department or None,
                receiver_type="department" if department else "all_users",
                is_broadcast_optimized=True,
                created_via="ui",
                metadata={"broadcast_type": "department" if department else "global"},
            )
            if department:
                recipients = Student.objects.filter(
                    department=department, user__is_active=True
                ).values_list("user_id", flat=True)
                recipient_type = "department_broadcast"
            else:
                recipients = CustomUser.objects.filter(is_active=True).values_list(
                    "id", flat=True
                )
                recipient_type = "global_broadcast"
            recipient_count = recipients.count()
            if recipient_count == 0:
                message.delete()
                django_messages.error(
                    request, "No recipients found for this broadcast."
                )
                return redirect("messaging:send_broadcast")
            broadcast_recipients = [
                BroadcastRecipient(
                    message=message,
                    recipient_id=recipient_id,
                    receiver_type=recipient_type,
                    is_delivered=True,
                )
                for recipient_id in recipients
            ]
            if broadcast_recipients:
                BroadcastRecipient.objects.bulk_create(
                    broadcast_recipients, batch_size=1000
                )
            MessageRecipientGroup.objects.create(
                message=message,
                recipient_type="department" if department else "all_users",
                department=department or None,
                total_recipients=recipient_count,
                delivered_count=recipient_count,
                status="completed",
            )
            log_activity_util(
                user=request.user,
                action_type="broadcast_sent",
                message=message,
                ip_address=get_client_ip(request),
                metadata={
                    "recipient_count": recipient_count,
                    "department": department or "all",
                    "broadcast_type": "department" if department else "global",
                },
            )
            django_messages.success(
                request,
                f"Broadcast sent successfully to {recipient_count} recipient(s)!",
            )
            return redirect("messaging:sent_messages")
    else:
        form = BroadcastMessageForm()
    context = {"form": form}
    return render(request, "messaging/send_broadcast.html", context)


@login_required
def get_unread_count(request):
    private_count = Message.objects.filter(
        receiver=request.user, is_read=False, message_type="private", is_deleted=False
    ).count()
    broadcast_count = BroadcastRecipient.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    total_count = private_count + broadcast_count
    return JsonResponse({"count": total_count})


@login_required
@require_teacher_or_admin()
@require_not_restricted()
def send_department_broadcast(request):
    if request.method == "POST":
        form = DepartmentBroadcastForm(user=request.user, data=request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            department = form.cleaned_data["target_department"]
            message = Message.objects.create(
                sender=request.user,
                content=content,
                message_type="broadcast",
                receiver_type="department",
                department=department,
                is_broadcast_optimized=True,
                created_via="ui",
                metadata={"broadcast_type": "department"},
            )
            recipients = Student.objects.filter(
                department=department, user__is_active=True
            ).values_list("user_id", flat=True)
            recipient_count = recipients.count()
            if recipient_count == 0:
                message.delete()
                django_messages.error(
                    request, f"No students found in {department} department."
                )
                return redirect("messaging:send_message")
            broadcast_recipients = [
                BroadcastRecipient(
                    message=message,
                    recipient_id=recipient_id,
                    receiver_type="department_broadcast",
                    is_delivered=True,
                )
                for recipient_id in recipients
            ]
            BroadcastRecipient.objects.bulk_create(
                broadcast_recipients, batch_size=1000
            )
            MessageRecipientGroup.objects.create(
                message=message,
                recipient_type="department",
                department=department,
                total_recipients=recipient_count,
                delivered_count=recipient_count,
                status="completed",
            )
            log_activity_util(
                user=request.user,
                action_type="department_message_sent",
                message=message,
                ip_address=get_client_ip(request),
                metadata={"department": department, "recipient_count": recipient_count},
            )
            django_messages.success(
                request,
                f"Broadcast sent to {recipient_count} students in {department}!",
            )
            return redirect("messaging:sent_messages")
    else:
        form = DepartmentBroadcastForm(user=request.user)
    context = {"form": form}
    return render(request, "messaging/send_department_broadcast.html", context)


@login_required
@require_admin()
@require_not_restricted()
def send_global_broadcast(request):
    if request.method == "POST":
        form = GlobalBroadcastForm(user=request.user, data=request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            message = Message.objects.create(
                sender=request.user,
                content=content,
                message_type="broadcast",
                receiver_type="all_users",
                is_broadcast_optimized=True,
                created_via="ui",
                metadata={"broadcast_type": "global", "large_scale_operation": True},
            )
            recipients = CustomUser.objects.filter(is_active=True).values_list(
                "id", flat=True
            )
            recipient_count = recipients.count()
            broadcast_recipients = [
                BroadcastRecipient(
                    message=message,
                    recipient_id=recipient_id,
                    receiver_type="global_broadcast",
                    is_delivered=True,
                )
                for recipient_id in recipients
            ]
            BroadcastRecipient.objects.bulk_create(
                broadcast_recipients, batch_size=1000
            )
            MessageRecipientGroup.objects.create(
                message=message,
                recipient_type="all_users",
                total_recipients=recipient_count,
                delivered_count=recipient_count,
                status="completed",
            )
            log_activity_util(
                user=request.user,
                action_type="broadcast_sent",
                message=message,
                ip_address=get_client_ip(request),
                metadata={
                    "recipient_count": recipient_count,
                    "broadcast_type": "global",
                    "large_scale_operation": True,
                },
            )
            django_messages.success(
                request, f"Global broadcast sent to {recipient_count} users!"
            )
            return redirect("messaging:sent_messages")
    else:
        form = GlobalBroadcastForm(user=request.user)
    context = {"form": form}
    return render(request, "messaging/send_global_broadcast.html", context)


def mark_broadcast_as_read(request, message_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    try:
        broadcast_recipient = BroadcastRecipient.objects.get(
            message_id=message_id, recipient=request.user
        )
        broadcast_recipient.is_read = True
        broadcast_recipient.read_at = timezone.now()
        broadcast_recipient.save(update_fields=["is_read", "read_at"])
        return JsonResponse({"success": True})
    except BroadcastRecipient.DoesNotExist:
        return JsonResponse({"error": "Broadcast not found"}, status=404)


@login_required
@require_admin()
def admin_messages_list(request):
    messages_qs = Message.objects.select_related(
        "sender", "receiver", "deleted_by"
    ).order_by("-timestamp")
    sender_id = request.GET.get("sender")
    receiver_id = request.GET.get("receiver")
    message_type = request.GET.get("message_type")
    receiver_type = request.GET.get("receiver_type")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    show_deleted_only = request.GET.get("deleted_only")
    show_unread_only = request.GET.get("unread_only")
    if sender_id:
        messages_qs = messages_qs.filter(sender_id=sender_id)
    if receiver_id:
        messages_qs = messages_qs.filter(receiver_id=receiver_id)
    if message_type:
        messages_qs = messages_qs.filter(message_type=message_type)
    if receiver_type:
        messages_qs = messages_qs.filter(receiver_type=receiver_type)
    if date_from:
        messages_qs = messages_qs.filter(timestamp__gte=date_from)
    if date_to:
        messages_qs = messages_qs.filter(timestamp__lte=date_to)
    if show_deleted_only:
        messages_qs = messages_qs.filter(is_deleted=True)
    if show_unread_only:
        messages_qs = messages_qs.filter(is_read=False)
    paginator = Paginator(messages_qs, 50)
    page_number = request.GET.get("page", 1)
    messages_page = paginator.get_page(page_number)
    context = {
        "messages": messages_page,
        "total_count": paginator.count,
        "deleted_count": Message.objects.filter(is_deleted=True).count(),
    }
    return render(request, "messaging/admin_messages_list.html", context)


@login_required
@require_admin()
def delete_message(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        message = Message.objects.get(pk=pk)
        message.soft_delete(request.user)
        log_activity_util(
            user=request.user,
            action_type="message_deleted",
            message=message,
            ip_address=get_client_ip(request),
            metadata={"message_id": pk},
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Message deleted"})
        django_messages.success(request, "Message deleted successfully.")
        return redirect("messaging:admin_messages_list")
    except Message.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Message not found"}, status=404)
        django_messages.error(request, "Message not found.")
        return redirect("messaging:admin_messages_list")


@login_required
@require_admin()
def recover_message(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        message = Message.objects.get(pk=pk)
        message.recover()
        log_activity_util(
            user=request.user,
            action_type="message_recovered",
            message=message,
            ip_address=get_client_ip(request),
            metadata={"message_id": pk},
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Message recovered"})
        django_messages.success(request, "Message recovered successfully.")
        return redirect("messaging:admin_messages_list")
    except Message.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Message not found"}, status=404)
        django_messages.error(request, "Message not found.")
        return redirect("messaging:admin_messages_list")


@login_required
@require_admin()
def admin_users_list(request):
    users_qs = CustomUser.objects.annotate(
        restriction_count=Count("restrictions", filter=Q(restrictions__is_active=True))
    ).order_by("-last_login")
    role = request.GET.get("role")
    department = request.GET.get("department")
    has_restrictions = request.GET.get("has_restrictions")
    is_active_filter = request.GET.get("is_active")
    if role:
        users_qs = users_qs.filter(role=role)
    if department:
        users_qs = users_qs.filter(student__department=department)
    if has_restrictions == "yes":
        users_qs = users_qs.filter(restriction_count__gt=0)
    elif has_restrictions == "no":
        users_qs = users_qs.filter(restriction_count=0)
    if is_active_filter == "active":
        users_qs = users_qs.filter(is_active=True)
    elif is_active_filter == "inactive":
        users_qs = users_qs.filter(is_active=False)
    paginator = Paginator(users_qs, 50)
    page_number = request.GET.get("page", 1)
    users_page = paginator.get_page(page_number)
    departments = Student.objects.values_list("department", flat=True).distinct()
    form = AdminUserActionForm()
    context = {
        "users": users_page,
        "total_users": paginator.count,
        "restricted_count": CustomUser.objects.filter(restrictions__is_active=True)
        .distinct()
        .count(),
        "department_choices": departments,
        "page_obj": users_page,
        "is_paginated": users_page.has_other_pages(),
        "form": form,
    }
    return render(request, "messaging/admin_users_list.html", context)


@login_required
@require_admin()
def ban_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        user = CustomUser.objects.get(id=user_id)
        reason = request.POST.get("reason", "").strip()
        expiration_days = request.POST.get("expiration_days")
        if not reason:
            error_msg = "Reason is required for banning a user."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": error_msg}, status=400)
            django_messages.error(request, error_msg)
            return redirect("messaging:admin_users_list")
        expires_at = None
        if expiration_days:
            try:
                expires_at = timezone.now() + timedelta(days=int(expiration_days))
            except ValueError:
                error_msg = "Invalid expiration days value."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": error_msg}, status=400)
                django_messages.error(request, error_msg)
                return redirect("messaging:admin_users_list")
        restriction, created = UserRestriction.objects.update_or_create(
            user=user,
            restriction_type="banned",
            defaults={
                "reason": reason,
                "restricted_by": request.user,
                "expires_at": expires_at,
                "is_active": True,
                "can_receive_broadcasts": False,
                "can_send_messages": False,
            },
        )
        log_activity_util(
            user=request.user,
            action_type="user_banned",
            target_user=user,
            ip_address=get_client_ip(request),
            metadata={"reason": reason, "expires_at": str(expires_at)},
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": f"User {user.username} has been banned."}
            )
        django_messages.success(request, f"User {user.username} has been banned.")
        return redirect("messaging:admin_users_list")
    except CustomUser.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "User not found"}, status=404)
        django_messages.error(request, "User not found.")
        return redirect("messaging:admin_users_list")


@login_required
@require_admin()
def unban_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        user = CustomUser.objects.get(id=user_id)
        ban_count = UserRestriction.objects.filter(
            user=user, restriction_type="banned"
        ).update(is_active=False)
        if ban_count == 0:
            error_msg = f"User {user.username} is not banned."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": error_msg}, status=400)
            django_messages.warning(request, error_msg)
            return redirect("messaging:admin_users_list")
        log_activity_util(
            user=request.user,
            action_type="user_unbanned",
            target_user=user,
            ip_address=get_client_ip(request),
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": f"User {user.username} has been unbanned."}
            )
        django_messages.success(request, f"User {user.username} has been unbanned.")
        return redirect("messaging:admin_users_list")
    except CustomUser.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "User not found"}, status=404)
        django_messages.error(request, "User not found.")
        return redirect("messaging:admin_users_list")


@login_required
@require_admin()
def mute_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        user = CustomUser.objects.get(id=user_id)
        reason = request.POST.get("reason", "").strip()
        expiration_days = request.POST.get("expiration_days")
        if not reason:
            error_msg = "Reason is required for muting a user."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": error_msg}, status=400)
            django_messages.error(request, error_msg)
            return redirect("messaging:admin_users_list")
        expires_at = None
        if expiration_days:
            try:
                expires_at = timezone.now() + timedelta(days=int(expiration_days))
            except ValueError:
                error_msg = "Invalid expiration days value."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": error_msg}, status=400)
                django_messages.error(request, error_msg)
                return redirect("messaging:admin_users_list")
        restriction, created = UserRestriction.objects.update_or_create(
            user=user,
            restriction_type="muted",
            defaults={
                "reason": reason,
                "restricted_by": request.user,
                "expires_at": expires_at,
                "is_active": True,
                "can_receive_broadcasts": True,
                "can_send_messages": False,
            },
        )
        log_activity_util(
            user=request.user,
            action_type="user_muted",
            target_user=user,
            ip_address=get_client_ip(request),
            metadata={"reason": reason, "expires_at": str(expires_at)},
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": f"User {user.username} has been muted."}
            )
        django_messages.success(request, f"User {user.username} has been muted.")
        return redirect("messaging:admin_users_list")
    except CustomUser.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "User not found"}, status=404)
        django_messages.error(request, "User not found.")
        return redirect("messaging:admin_users_list")


@login_required
@require_admin()
def unmute_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        user = CustomUser.objects.get(id=user_id)
        mute_count = UserRestriction.objects.filter(
            user=user, restriction_type="muted"
        ).update(is_active=False)
        if mute_count == 0:
            error_msg = f"User {user.username} is not muted."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": error_msg}, status=400)
            django_messages.warning(request, error_msg)
            return redirect("messaging:admin_users_list")
        log_activity_util(
            user=request.user,
            action_type="user_unmuted",
            target_user=user,
            ip_address=get_client_ip(request),
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": f"User {user.username} has been unmuted."}
            )
        django_messages.success(request, f"User {user.username} has been unmuted.")
        return redirect("messaging:admin_users_list")
    except CustomUser.DoesNotExist:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "User not found"}, status=404)
        django_messages.error(request, "User not found.")
        return redirect("messaging:admin_users_list")


@login_required
@require_admin()
def user_activity_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    activity_logs = ActivityLog.objects.filter(user=user).order_by("-created_at")[:100]
    restrictions = UserRestriction.objects.filter(user=user, is_active=True)
    sent_count = Message.objects.filter(sender=user).count()
    received_count = Message.objects.filter(receiver=user).count()
    context = {
        "user": user,
        "activity_logs": activity_logs,
        "restrictions": restrictions,
        "sent_count": sent_count,
        "received_count": received_count,
    }
    return render(request, "messaging/user_activity_detail.html", context)


@login_required
@require_admin()
def activity_log_list(request):
    logs_qs = ActivityLog.objects.select_related(
        "user", "target_user", "message"
    ).order_by("-created_at")
    action_type = request.GET.get("action_type")
    user_id = request.GET.get("user")
    target_user_id = request.GET.get("target_user")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    search = request.GET.get("search")
    if action_type:
        logs_qs = logs_qs.filter(action_type=action_type)
    if user_id:
        logs_qs = logs_qs.filter(user_id=user_id)
    if target_user_id:
        logs_qs = logs_qs.filter(target_user_id=target_user_id)
    if date_from:
        logs_qs = logs_qs.filter(created_at__gte=date_from)
    if date_to:
        logs_qs = logs_qs.filter(created_at__lte=date_to)
    if search:
        logs_qs = logs_qs.filter(
            Q(user__username__icontains=search)
            | Q(target_user__username__icontains=search)
            | Q(metadata__icontains=search)
        )
    paginator = Paginator(logs_qs, 100)
    page_number = request.GET.get("page", 1)
    logs_page = paginator.get_page(page_number)
    context = {
        "activity_logs": logs_page,
        "total_count": paginator.count,
        "page_obj": logs_page,
        "is_paginated": logs_page.has_other_pages(),
    }
    return render(request, "messaging/activity_log_list.html", context)


@login_required
@require_admin()
def admin_control_panel(request):
    context = {}
    return render(request, "messaging/admin_control_panel.html", context)


@login_required
@require_admin()
def admin_dashboard(request):
    import json
    from django.db.models import Sum

    total_messages = Message.objects.count()
    broadcasts = Message.objects.filter(message_type="broadcast").count()
    private_messages = Message.objects.filter(message_type="private").count()
    deleted_count = Message.objects.filter(is_deleted=True).count()
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    restricted_users = (
        CustomUser.objects.filter(restrictions__is_active=True).distinct().count()
    )
    seven_days_ago = timezone.now() - timedelta(days=7)
    volume_data = (
        Message.objects.filter(timestamp__gte=seven_days_ago)
        .extra(select={"date": "DATE(timestamp)"})
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    most_active = CustomUser.objects.annotate(
        message_count=Count("sent_messages")
    ).order_by("-message_count")[:10]
    recent_actions = ActivityLog.objects.filter(
        action_type__in=["user_banned", "user_muted", "user_unbanned", "user_unmuted"]
    ).order_by("-created_at")[:10]
    failed_broadcasts = MessageRecipientGroup.objects.filter(status="failed").order_by(
        "-started_at"
    )[:10]
    chart_days = json.dumps([str(v["date"]) for v in volume_data])
    chart_volumes = json.dumps([v["count"] for v in volume_data])
    message_types = Message.objects.values("message_type").annotate(count=Count("id"))
    message_type_labels = json.dumps(
        [mt["message_type"].title() for mt in message_types]
    )
    message_type_data = json.dumps([mt["count"] for mt in message_types])
    total_conversations = (
        Message.objects.values("sender", "receiver").distinct().count()
    )
    total_active_users = (
        CustomUser.objects.filter(
            Q(sent_messages__isnull=False) | Q(received_messages__isnull=False)
        )
        .distinct()
        .count()
    )
    messages_this_week = Message.objects.filter(timestamp__gte=seven_days_ago).count()
    context = {
        "total_messages": total_messages,
        "broadcasts": broadcasts,
        "private_messages": private_messages,
        "deleted_count": deleted_count,
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_active_users": total_active_users,
        "active_users": active_users,
        "restricted_users": restricted_users,
        "messages_this_week": messages_this_week,
        "volume_data": list(volume_data),
        "most_active": most_active,
        "top_active_users": most_active,
        "recent_admin_actions": recent_actions,
        "recent_actions": recent_actions,
        "failed_broadcasts": failed_broadcasts,
        "chart_days": chart_days,
        "chart_volumes": chart_volumes,
        "message_type_labels": message_type_labels,
        "message_type_data": message_type_data,
    }
    return render(request, "messaging/admin_dashboard.html", context)


@login_required
@require_admin_only()
def teacher_management_dashboard(request):
    from students.models import Teacher, SalaryPayment
    from django.db.models import Q, Count, Sum
    from django.utils import timezone
    from datetime import timedelta

    teachers = Teacher.objects.select_related("user").all()
    total_teachers = teachers.count()
    current_month = timezone.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    salary_due_this_month = teachers.filter(
        salary_status="due", last_paid_date__lt=current_month
    ).count()
    total_paid_this_month = (
        SalaryPayment.objects.filter(
            payment_date__gte=current_month, payment_date__lt=next_month
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    recent_payments = SalaryPayment.objects.select_related(
        "teacher__user", "processed_by"
    ).order_by("-payment_date")[:10]
    dept_counts = (
        teachers.values("department").annotate(count=Count("id")).order_by("department")
    )
    context = {
        "total_teachers": total_teachers,
        "salary_due_this_month": salary_due_this_month,
        "total_paid_this_month": total_paid_this_month,
        "recent_payments": recent_payments,
        "dept_counts": dept_counts,
    }
    return render(request, "messaging/teacher_management.html", context)


@login_required
@require_admin_only()
def teacher_list(request):
    from students.models import Teacher

    form = TeacherFilterForm(request.GET or None)
    teachers = Teacher.objects.select_related("user").all()
    if form.is_valid():
        if form.cleaned_data.get("department"):
            teachers = teachers.filter(department=form.cleaned_data["department"])
        if form.cleaned_data.get("salary_status"):
            teachers = teachers.filter(salary_status=form.cleaned_data["salary_status"])
        if form.cleaned_data.get("search"):
            search = form.cleaned_data["search"]
            teachers = teachers.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(employee_id__icontains=search)
            )
    sort_by = request.GET.get("sort_by", "-user__first_name")
    teachers = teachers.order_by(sort_by)
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get("page")
    teachers_page = paginator.get_page(page_number)
    context = {
        "form": form,
        "teachers": teachers_page,
        "page_obj": teachers_page,
    }
    return render(request, "messaging/teacher_list.html", context)


@login_required
@require_admin_only()
def teacher_add(request):
    from students.models import Teacher

    if request.method == "POST":
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                username=form.cleaned_data["email"],
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password"],
                role="teacher",
            )
            teacher = Teacher.objects.create(
                user=user,
                employee_id=form.cleaned_data["employee_id"],
                department=form.cleaned_data["department"],
                designation=form.cleaned_data["designation"],
                salary_amount=form.cleaned_data["salary_amount"],
                salary_status="due",
            )
            log_activity_util(
                user=request.user,
                action_type="teacher_added",
                target_user=user,
                ip_address=get_client_ip(request),
                metadata={"teacher_id": teacher.id, "department": teacher.department},
            )
            django_messages.success(
                request, f"Teacher {user.get_full_name()} added successfully!"
            )
            return redirect("messaging:teacher_detail", teacher_id=teacher.id)
    else:
        form = TeacherCreationForm()
    context = {"form": form}
    return render(request, "messaging/teacher_form.html", context)


@login_required
@require_admin_only()
def teacher_edit(request, teacher_id):
    from students.models import Teacher

    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = TeacherUpdateForm(request.POST)
        if form.is_valid():
            teacher.user.first_name = form.cleaned_data["first_name"]
            teacher.user.last_name = form.cleaned_data["last_name"]
            if form.cleaned_data.get("email"):
                teacher.user.email = form.cleaned_data["email"]
            teacher.user.save()
            teacher.department = form.cleaned_data["department"]
            teacher.designation = form.cleaned_data["designation"]
            teacher.salary_amount = form.cleaned_data["salary_amount"]
            if form.cleaned_data.get("phone"):
                teacher.phone = form.cleaned_data["phone"]
            teacher.save()
            log_activity_util(
                user=request.user,
                action_type="teacher_updated",
                target_user=teacher.user,
                ip_address=get_client_ip(request),
                metadata={"teacher_id": teacher.id},
            )
            django_messages.success(request, "Teacher updated successfully!")
            return redirect("messaging:teacher_detail", teacher_id=teacher.id)
    else:
        form = TeacherUpdateForm(
            initial={
                "first_name": teacher.user.first_name,
                "last_name": teacher.user.last_name,
                "email": teacher.user.email,
                "phone": teacher.phone,
                "department": teacher.department,
                "designation": teacher.designation,
                "salary_amount": teacher.salary_amount,
            }
        )
    context = {"form": form, "teacher": teacher}
    return render(request, "messaging/teacher_form.html", context)


@login_required
@require_admin_only()
def teacher_delete(request, teacher_id):
    from students.models import Teacher

    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        teacher_name = teacher.user.get_full_name()
        teacher.user.is_active = False
        teacher.user.save()
        log_activity_util(
            user=request.user,
            action_type="teacher_deleted",
            target_user=teacher.user,
            ip_address=get_client_ip(request),
            metadata={"teacher_id": teacher.id},
        )
        django_messages.success(
            request, f"Teacher {teacher_name} has been deactivated."
        )
        return redirect("messaging:teacher_list")
    context = {"teacher": teacher}
    return render(request, "messaging/teacher_confirm_delete.html", context)


@login_required
@require_admin_only()
def teacher_detail(request, teacher_id):
    from students.models import Teacher, SalaryPayment

    teacher = get_object_or_404(Teacher, id=teacher_id)
    salary_payments = (
        SalaryPayment.objects.filter(teacher=teacher)
        .select_related("processed_by")
        .order_by("-payment_date")
    )
    teacher_messages = Message.objects.filter(sender=teacher.user).order_by(
        "-timestamp"
    )[:20]
    context = {
        "teacher": teacher,
        "salary_payments": salary_payments,
        "teacher_messages": teacher_messages,
    }
    return render(request, "messaging/teacher_detail.html", context)


@login_required
@require_admin_only()
@log_activity(action_type="teacher_salary_paid", include_metadata=True)
def teacher_update_salary(request, teacher_id):
    from students.models import Teacher, SalaryPayment
    from django.utils import timezone

    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = SalaryPaymentForm(request.POST)
        if form.is_valid():
            payment = SalaryPayment.objects.create(
                teacher=teacher,
                amount=form.cleaned_data["amount"],
                payment_date=form.cleaned_data["payment_date"],
                payment_method=form.cleaned_data["payment_method"],
                reference_number=form.cleaned_data.get("reference_number", ""),
                notes=form.cleaned_data.get("notes", ""),
                processed_by=request.user,
            )
            teacher.salary_status = form.cleaned_data["salary_status"]
            teacher.last_paid_date = form.cleaned_data["payment_date"]
            teacher.save()
            log_activity_util(
                user=request.user,
                action_type="teacher_salary_paid",
                target_user=teacher.user,
                message=payment,
                ip_address=get_client_ip(request),
                metadata={
                    "teacher_id": teacher.id,
                    "amount": str(payment.amount),
                    "payment_date": payment.payment_date.isoformat(),
                    "salary_status": teacher.salary_status,
                },
            )
            django_messages.success(
                request,
                f"Salary of ₹{payment.amount} recorded and status updated to {teacher.get_salary_status_display()} for {teacher.user.get_full_name()}",
            )
            return redirect("messaging:teacher_detail", teacher_id=teacher.id)
    else:
        form = SalaryPaymentForm(initial={"payment_date": timezone.now().date()})
    context = {"form": form, "teacher": teacher}
    return render(request, "messaging/salary_payment_form.html", context)


@login_required
@require_admin_only()
def teacher_salary_history(request):
    from students.models import SalaryPayment

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    teacher_filter = request.GET.get("teacher")
    payments = SalaryPayment.objects.select_related(
        "teacher__user", "processed_by"
    ).order_by("-payment_date")
    if date_from:
        from datetime import datetime

        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        payments = payments.filter(payment_date__gte=date_from_obj)
    if date_to:
        from datetime import datetime

        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        payments = payments.filter(payment_date__lte=date_to_obj)
    if teacher_filter:
        payments = payments.filter(teacher_id=teacher_filter)
    paginator = Paginator(payments, 50)
    page_number = request.GET.get("page")
    payments_page = paginator.get_page(page_number)
    from students.models import Teacher

    teachers = Teacher.objects.all().order_by("user__first_name")
    context = {
        "payments": payments_page,
        "page_obj": payments_page,
        "teachers": teachers,
        "date_from": date_from,
        "date_to": date_to,
        "teacher_filter": teacher_filter,
    }
    return render(request, "messaging/salary_history.html", context)


@login_required
@require_admin_only()
def teacher_edit_salary_status(request, teacher_id):
    from students.models import Teacher

    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = TeacherSalaryStatusForm(request.POST)
        if form.is_valid():
            old_status = teacher.salary_status
            new_status = form.cleaned_data["salary_status"]
            teacher.salary_status = new_status
            teacher.save(update_fields=["salary_status"])
            log_activity_util(
                user=request.user,
                action_type="teacher_salary_status_updated",
                target_user=teacher.user,
                ip_address=get_client_ip(request),
                metadata={
                    "teacher_id": teacher.id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "notes": form.cleaned_data.get("notes", ""),
                },
            )
            django_messages.success(
                request,
                f"Salary status updated to {teacher.get_salary_status_display()} for {teacher.user.get_full_name()}",
            )
            return redirect("messaging:teacher_detail", teacher_id=teacher.id)
    else:
        form = TeacherSalaryStatusForm(initial={"salary_status": teacher.salary_status})
    context = {"form": form, "teacher": teacher}
    return render(request, "messaging/edit_salary_status.html", context)


@login_required
@require_admin_only()
def teacher_quick_payment(request, teacher_id):
    from students.models import Teacher, SalaryPayment
    from django.utils import timezone
    from django.http import JsonResponse

    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = QuickSalaryPaymentForm(request.POST)
        if form.is_valid():
            payment = SalaryPayment.objects.create(
                teacher=teacher,
                amount=form.cleaned_data["amount"],
                payment_date=form.cleaned_data["payment_date"],
                payment_method=form.cleaned_data["payment_method"],
                reference_number=form.cleaned_data.get("reference_number", ""),
                processed_by=request.user,
            )
            teacher.salary_status = "paid"
            teacher.last_paid_date = form.cleaned_data["payment_date"]
            teacher.save()
            log_activity_util(
                user=request.user,
                action_type="teacher_salary_paid",
                target_user=teacher.user,
                message=payment,
                ip_address=get_client_ip(request),
                metadata={
                    "teacher_id": teacher.id,
                    "amount": str(payment.amount),
                    "payment_date": payment.payment_date.isoformat(),
                },
            )
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Payment of ₹{payment.amount} recorded successfully",
                    }
                )
            django_messages.success(
                request,
                f"Payment of ₹{payment.amount} recorded for {teacher.user.get_full_name()}",
            )
            return redirect("messaging:teacher_detail", teacher_id=teacher.id)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )
    else:
        form = QuickSalaryPaymentForm(initial={"payment_date": timezone.now().date()})
    context = {"form": form, "teacher": teacher}
    return render(request, "messaging/quick_payment_form.html", context)
