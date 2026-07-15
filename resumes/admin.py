from django.contrib import admin
from .models import Resume, ResumeVersion

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'current_version', 'created_at', 'updated_at')
    search_fields = ('title', 'user__email')
    list_filter = ('created_at', 'updated_at')

@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'version_number', 'created_at')
    search_fields = ('resume__title', 'resume__user__email')
    list_filter = ('created_at',)
