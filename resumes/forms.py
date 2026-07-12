import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('title', 'file')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.docx']
            if ext not in valid_extensions:
                raise ValidationError(_('Unsupported file extension. Only PDF and DOCX files are allowed.'))

            # Check file size (5MB limit)
            max_size = 5 * 1024 * 1024  # 5MB
            if file.size > max_size:
                raise ValidationError(_('File size exceeds the 5MB limit.'))
        return file
