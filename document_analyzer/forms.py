from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading a document."""
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        } 