from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def resume_upload_path(instance, filename):
    return f'resumes/user_{instance.user.id}/{filename}'


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    original_filename = models.CharField(max_length=255, blank=True)
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.original_filename} ({self.user.username})'


class Analysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_description = models.TextField()

    # Scores (0-100)
    similarity_score = models.FloatField(default=0)
    ats_score = models.FloatField(default=0)
    overall_score = models.FloatField(default=0)

    # JSON-serialized lists
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    ats_issues = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analyses'

    def __str__(self):
        return f'Analysis #{self.id} for {self.resume.original_filename}'
