from django.contrib import admin
from .models import Resume, Analysis


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename', 'user__username')


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'overall_score', 'similarity_score', 'ats_score', 'created_at')
    list_filter = ('created_at',)
