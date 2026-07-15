from django.contrib import admin
from .models import ATSFeedback, AIActionLog, GeneratedResume

@admin.register(ATSFeedback)
class ATSFeedbackAdmin(admin.ModelAdmin):
    list_display = ('resume', 'score', 'created_at')
    search_fields = ('resume__title', 'resume__user__email')
    list_filter = ('created_at', 'score')

@admin.register(AIActionLog)
class AIActionLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'target_name', 'tokens_used', 'latency_ms', 'status', 'created_at')
    search_fields = ('target_name', 'action')
    list_filter = ('status', 'action', 'created_at')

@admin.register(GeneratedResume)
class GeneratedResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'target_job_field', 'target_job_role', 'template', 'ats_score', 'is_ai_generated', 'created_at')
    search_fields = ('title', 'user__email', 'target_job_role')
    list_filter = ('target_job_field', 'template', 'is_ai_generated', 'created_at')
