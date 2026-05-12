from django.urls import path
from . import views
app_name = "timetable"
urlpatterns = [
    path("", views.timetable_view, name="timetable"),
    path("add/", views.add_timeslot, name="add_timeslot"),
    path("edit/<int:pk>/", views.edit_timeslot, name="edit_timeslot"),
    path("delete/<int:pk>/", views.delete_timeslot, name="delete_timeslot"),
    path("api/subjects/", views.get_subjects_by_dept_semester, name="api_subjects"),
]
