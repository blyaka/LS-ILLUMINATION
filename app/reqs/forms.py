from django import forms
from .models import Request
import time

class RequestForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput())
    ts = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Request
        fields = ['name', 'phone', 'email', 'message']

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
