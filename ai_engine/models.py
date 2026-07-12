from django.db import models
from resumes.models import Resume

class ATSFeedback(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    score = models.IntegerField()
    job_description = models.TextField(blank=True, default='')
    feedback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ATS Scan for {self.resume.title} - Score: {self.score}%"

class AIActionLog(models.Model):
    """Tracks every AI operation for real-time admin monitoring."""
    ACTION_CHOICES = [
        ('ats_scan',        'ATS Scan'),
        ('bullet_improver', 'Bullet Improver'),
        ('cover_letter',    'Cover Letter'),
        ('career_coach',    'Career Coach'),
        ('interview_prep',  'Interview Q Generator'),
        ('job_matching',    'Skills Gap Analysis'),
    ]
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error',   'Error'),
        ('mocked',  'Mocked'),
    ]

    action      = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_name = models.CharField(max_length=255, blank=True, default='')
    tokens_used = models.IntegerField(default=0)
    latency_ms  = models.FloatField(default=0)  # seconds
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='success')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_action_display()}] {self.target_name} - {self.status}"

