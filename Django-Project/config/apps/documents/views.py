from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import FileResponse
from django.db.models import Q
import mimetypes
from .models import Document
from .forms import DocumentUploadForm
@login_required
def documents_list(request):
    subject_filter = request.GET.get("subject")
    doc_type_filter = request.GET.get("type")
    documents = (
        Document.objects.all()
        .select_related("subject", "uploaded_by")
        .order_by("-uploaded_at")
    )
    if subject_filter:
        documents = documents.filter(subject__code=subject_filter)
    if doc_type_filter:
        documents = documents.filter(document_type=doc_type_filter)
    context = {
        "documents": documents,
        "selected_subject": subject_filter,
        "selected_type": doc_type_filter,
    }
    return render(request, "documents/documents_list.html", context)
@login_required
def upload_document(request):
    if not (request.user.is_staff or request.user.role == "teacher"):
        django_messages.error(request, "Only teachers and admins can upload documents.")
        return redirect("documents:documents_list")
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            django_messages.success(request, "Document uploaded successfully!")
            return redirect("documents:documents_list")
    else:
        form = DocumentUploadForm()
    context = {"form": form}
    return render(request, "documents/upload_document.html", context)
@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.increment_downloads()
    response = FileResponse(document.file.open("rb"))
    response["Content-Disposition"] = (
        f'attachment; filename="{document.file.name.split("/")[-1]}"'
    )
    return response
@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    context = {"document": document}
    return render(request, "documents/document_detail.html", context)
