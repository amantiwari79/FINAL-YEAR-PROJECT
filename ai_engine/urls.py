from django.urls import path
from . import views

urlpatterns = [
    path('ats-scan/<int:resume_id>/', views.ats_scan, name='ats_scan'),
    path('career-coach/', views.career_coach_view, name='career_coach'),
    path('interview-prep/<int:resume_id>/', views.interview_prep_view, name='interview_prep'),
    path('job-matching/', views.job_matching_view, name='job_matching'),
]
