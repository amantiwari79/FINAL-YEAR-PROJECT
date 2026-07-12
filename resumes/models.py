from django.db import models
from django.conf import settings

class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True, default='')
    parsed_data = models.JSONField(default=dict, blank=True)
    current_version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} (v{self.current_version})"

class ResumeVersion(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.IntegerField()
    file = models.FileField(upload_to='resumes/versions/')
    raw_text = models.TextField(blank=True, default='')
    parsed_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.resume.title} - Version {self.version_number}"
