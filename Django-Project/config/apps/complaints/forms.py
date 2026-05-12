from django import forms
from .models import Complaint
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["title", "description", "complaint_type"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Complaint title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your complaint...",
                }
            ),
            "complaint_type": forms.Select(attrs={"class": "form-control"}),
        }
class ResolutionForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["status", "resolution_notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "resolution_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add resolution notes...",
                }
            ),
        }
