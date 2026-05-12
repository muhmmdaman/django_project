from django.urls import path
from . import views

app_name = "messaging"
urlpatterns = [
    path("inbox/", views.inbox, name="inbox"),
    path("sent/", views.sent_messages, name="sent_messages"),
    path("send/", views.send_message, name="send_message"),
    path("message/<int:pk>/", views.message_detail, name="message_detail"),
    path("broadcast/", views.send_broadcast, name="send_broadcast"),
    path(
        "broadcast/department/",
        views.send_department_broadcast,
        name="send_department_broadcast",
    ),
    path(
        "broadcast/global/", views.send_global_broadcast, name="send_global_broadcast"
    ),
    path(
        "broadcast/<int:message_id>/read/",
        views.mark_broadcast_as_read,
        name="mark_broadcast_as_read",
    ),
    path("admin/", views.admin_control_panel, name="admin_control_panel"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/messages/", views.admin_messages_list, name="admin_messages_list"),
    path(
        "admin/messages/<int:pk>/delete/", views.delete_message, name="delete_message"
    ),
    path(
        "admin/messages/<int:pk>/recover/",
        views.recover_message,
        name="recover_message",
    ),
    path("admin/users/", views.admin_users_list, name="admin_users_list"),
    path("admin/users/<int:user_id>/ban/", views.ban_user, name="ban_user"),
    path("admin/users/<int:user_id>/unban/", views.unban_user, name="unban_user"),
    path("admin/users/<int:user_id>/mute/", views.mute_user, name="mute_user"),
    path("admin/users/<int:user_id>/unmute/", views.unmute_user, name="unmute_user"),
    path(
        "admin/users/<int:user_id>/activity/",
        views.user_activity_detail,
        name="user_activity_detail",
    ),
    path("admin/activity/", views.activity_log_list, name="activity_log_list"),
    path("admin/teachers/", views.teacher_list, name="teacher_list"),
    path(
        "admin/teachers/dashboard/",
        views.teacher_management_dashboard,
        name="teacher_management_dashboard",
    ),
    path("admin/teachers/add/", views.teacher_add, name="teacher_add"),
    path(
        "admin/teachers/<int:teacher_id>/", views.teacher_detail, name="teacher_detail"
    ),
    path(
        "admin/teachers/<int:teacher_id>/edit/", views.teacher_edit, name="teacher_edit"
    ),
    path(
        "admin/teachers/<int:teacher_id>/delete/",
        views.teacher_delete,
        name="teacher_delete",
    ),
    path(
        "admin/teachers/<int:teacher_id>/salary/",
        views.teacher_update_salary,
        name="teacher_update_salary",
    ),
    path("admin/salary-history/", views.teacher_salary_history, name="salary_history"),
    path(
        "admin/teachers/<int:teacher_id>/edit-salary-status/",
        views.teacher_edit_salary_status,
        name="teacher_edit_salary_status",
    ),
    path(
        "admin/teachers/<int:teacher_id>/quick-payment/",
        views.teacher_quick_payment,
        name="teacher_quick_payment",
    ),
    path("api/unread-count/", views.get_unread_count, name="unread_count"),
]
