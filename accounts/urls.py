from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Custom Admin Control Panel Routes
    path('admin-panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/toggle-active/<int:user_id>/', admin_views.toggle_user_active, name='toggle_user_active'),
    path('admin-panel/toggle-staff/<int:user_id>/', admin_views.toggle_user_staff, name='toggle_user_staff'),
    
    # Static Info and Support Routes
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_conditions, name='terms_conditions'),
    path('support/', views.contact_support, name='contact_support'),
    path('about/', views.about_view, name='about'),
    path('features/', views.features_view, name='features'),
]
