from django.urls import path
from . import views
app_name = "analytics"
urlpatterns = [
    path("", views.analytics_dashboard, name="dashboard"),
    path("performance/", views.performance_details, name="performance_details"),
    path("risk/", views.risk_analysis, name="risk_analysis"),
    path("admin/", views.admin_analytics, name="admin_analytics"),
]
