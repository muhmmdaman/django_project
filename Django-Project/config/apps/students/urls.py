from django.urls import path
from . import views, api
app_name = "students"
urlpatterns = [
    path("", views.StudentListView.as_view(), name="student_list"),
    path("add/", views.add_student, name="add_student"),
    path("marks/add/", views.add_marks, name="add_marks"),
    path("upload/students/", views.upload_students_csv, name="upload_students"),
    path("upload/marks/", views.upload_marks_csv, name="upload_marks"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/report/", views.download_report, name="download_report"),
    path("api/profile/", api.api_student_profile, name="api_profile"),
    path("api/marks/", api.api_student_marks, name="api_marks"),
    path("api/performance/", api.api_student_performance, name="api_performance"),
    path(
        "api/department-stats/", api.api_department_stats, name="api_department_stats"
    ),
    path(
        "api/risk-distribution/",
        api.api_risk_distribution,
        name="api_risk_distribution",
    ),
    path(
        "teacher/documents/upload/",
        views.teacher_upload_subject_document,
        name="teacher_upload_document",
    ),
    path(
        "teacher/documents/",
        views.teacher_documents_list,
        name="teacher_documents_list",
    ),
    path(
        "admin/documents/approval/",
        views.admin_document_approval,
        name="admin_document_approval",
    ),
    path(
        "admin/documents/<int:document_id>/approve-reject/",
        views.document_approve_reject,
        name="document_approve_reject",
    ),
    path(
        "admin/teachers/salary/",
        views.teacher_salary_list,
        name="teacher_salary_list",
    ),
    path(
        "admin/teachers/<int:teacher_id>/salary/edit/",
        views.edit_teacher_salary,
        name="edit_teacher_salary",
    ),
    path(
        "admin/teachers/<int:teacher_id>/salary/payment/add/",
        views.add_salary_payment,
        name="add_salary_payment",
    ),
    path(
        "admin/teachers/<int:teacher_id>/salary/detail/",
        views.teacher_salary_detail,
        name="teacher_salary_detail",
    ),
]
