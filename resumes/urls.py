from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('<int:pk>/new-version/', views.upload_new_version, name='upload_new_version'),
    path('<int:pk>/delete/', views.delete_resume, name='delete_resume'),
]
