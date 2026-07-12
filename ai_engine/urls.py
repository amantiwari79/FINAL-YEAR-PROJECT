from django.urls import path
from . import views

urlpatterns = [
    path('ats-scan/<int:resume_id>/', views.ats_scan, name='ats_scan'),
    path('bullet-improver/<int:resume_id>/', views.bullet_improver, name='bullet_improver'),
    path('cover-letter/<int:resume_id>/', views.cover_letter_view, name='cover_letter'),
    path('career-coach/', views.career_coach_view, name='career_coach'),
    path('interview-prep/<int:resume_id>/', views.interview_prep_view, name='interview_prep'),
]
