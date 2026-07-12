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
