from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Resume


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': '.pdf', 'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        max_size_mb = 5
        if file.size > max_size_mb * 1024 * 1024:
            raise forms.ValidationError(f"File too large. Max size is {max_size_mb}MB.")
        return file


class JobDescriptionForm(forms.Form):
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'placeholder': 'Paste the job description here...',
            'class': 'form-control',
        }),
        min_length=30,
        label='Job Description',
    )
