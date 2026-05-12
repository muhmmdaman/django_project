from django.urls import path
from . import views
app_name = "complaints"
urlpatterns = [
    path("", views.complaints_list, name="complaints_list"),
    path("submit/", views.submit_complaint, name="submit_complaint"),
    path("<int:pk>/", views.complaint_detail, name="complaint_detail"),
]
