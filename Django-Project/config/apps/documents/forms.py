from django import forms
from .models import Document
class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["subject", "title", "description", "document_type", "file"]
        widgets = {
            "subject": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Document title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief description...",
                }
            ),
            "document_type": forms.Select(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }
