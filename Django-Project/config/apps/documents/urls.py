from django.urls import path
from . import views
app_name = "documents"
urlpatterns = [
    path("", views.documents_list, name="documents_list"),
    path("upload/", views.upload_document, name="upload"),
    path("<int:pk>/", views.document_detail, name="detail"),
    path("<int:pk>/download/", views.download_document, name="download"),
]
