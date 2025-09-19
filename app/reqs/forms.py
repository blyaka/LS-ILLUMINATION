# reqs/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
from .models import Request
import time
import os

ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'text/plain',
    'application/zip',
}
MAX_FILE_SIZE = 12 * 1024 * 1024

class RequestForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput())
    ts = forms.IntegerField(widget=forms.HiddenInput())
    file = forms.FileField(required=False)

    class Meta:
        model = Request
        fields = ['name', 'phone', 'email', 'message', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'required': True}),
            'phone': forms.TextInput(attrs={'inputmode': 'tel', 'placeholder': '+7', 'required': True}),
            'email': forms.EmailInput(),
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_hp(self):
        if self.cleaned_data.get('hp'):
            raise forms.ValidationError('Spam blocked.')
        return ''

    def clean_ts(self):
        ts = self.cleaned_data.get('ts') or 0
        now = int(time.time())
        if now - ts < 2:
            raise forms.ValidationError('Too fast.')
        if now - ts > 1800:
            raise forms.ValidationError('Form expired.')
        return ts

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return None
        
        if f.size > MAX_FILE_SIZE:
            raise ValidationError('Файл слишком большой (макс. 10 МБ).')
        
        ctype = (getattr(f, 'content_type', '') or '').lower()
        if ctype not in ALLOWED_CONTENT_TYPES:
            raise ValidationError('Недопустимый тип файла.')
        
        base, ext = os.path.splitext(f.name)
        safe = get_valid_filename(base)[:80] + ext.lower()
        f.name = safe or 'file' + ext.lower()
        return f
