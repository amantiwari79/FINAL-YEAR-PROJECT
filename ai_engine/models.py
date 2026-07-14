from django.db import models
from django.conf import settings
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
        ('resume_generator','Resume Generator'),
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

class GeneratedResume(models.Model):
    TEMPLATE_CHOICES = [
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
        ('corporate', 'Corporate'),
        ('executive', 'Executive'),
        ('creative', 'Creative'),
    ]
    JOB_FIELD_CHOICES = [
        ('software_developer', 'Software Developer'),
        ('data_analyst', 'Data Analyst'),
        ('ai_ml_engineer', 'AI/ML Engineer'),
        ('web_developer', 'Web Developer'),
        ('cyber_security', 'Cyber Security'),
        ('cloud_engineer', 'Cloud Engineer'),
        ('devops_engineer', 'DevOps Engineer'),
        ('ui_ux_designer', 'UI/UX Designer'),
        ('graphic_designer', 'Graphic Designer'),
        ('digital_marketing', 'Digital Marketing'),
        ('hr', 'HR'),
        ('accountant', 'Accountant'),
        ('teacher', 'Teacher'),
        ('civil_engineer', 'Civil Engineer'),
        ('mechanical_engineer', 'Mechanical Engineer'),
        ('electrical_engineer', 'Electrical Engineer'),
        ('mba', 'MBA'),
        ('sales', 'Sales'),
        ('customer_support', 'Customer Support'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_resumes'
    )
    title = models.CharField(max_length=255)
    target_job_field = models.CharField(max_length=50, choices=JOB_FIELD_CHOICES)
    target_job_role = models.CharField(max_length=255)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='modern')
    input_data = models.JSONField(default=dict, blank=True)
    generated_content = models.JSONField(default=dict, blank=True)
    ats_score = models.IntegerField(default=0)
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"

