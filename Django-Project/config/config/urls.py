from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("analytics/", include("analytics.urls")),
    path("messages/", include("messaging.urls")),
    path("complaints/", include("complaints.urls")),
    path("documents/", include("documents.urls")),
    path("timetable/", include("timetable.urls")),
    path("", include("core.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
