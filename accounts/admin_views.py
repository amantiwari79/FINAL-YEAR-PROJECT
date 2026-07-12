from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from decouple import config
from resumes.models import Resume
from ai_engine.models import ATSFeedback
from ai_engine.utils import get_gemini_client

User = get_user_model()

def is_admin(user):
    """
    Checks if the user is staff or superuser.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    """
    Renders system statistics, API status checks, and a user accounts management table.
    """
    # 1. Gather System Statistics
    total_users = User.objects.count()
    total_resumes = Resume.objects.count()
    total_scans = ATSFeedback.objects.count()
    
    # 2. Inspect API Configuration
    gemini_key = config('GEMINI_API_KEY', default='')
    client = get_gemini_client()
    
    api_configured = client is not None
    if gemini_key:
        if len(gemini_key) > 10:
            masked_key = f"{gemini_key[:8]}...{gemini_key[-8:]}"
        else:
            masked_key = "Configured (Invalid Format)"
    else:
        masked_key = "Not Configured"
        
    # 3. Retrieve User Accounts with Resume Counts
    users = User.objects.annotate(resume_count=Count('resumes')).order_by('-date_joined')
    
    context = {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'total_scans': total_scans,
        'api_configured': api_configured,
        'masked_key': masked_key,
        'users_list': users,
        'gemini_model': 'gemini-2.5-flash'
    }
    return render(request, 'accounts/admin_panel.html', context)

@user_passes_test(is_admin, login_url='login')
def toggle_user_active(request, user_id):
    """
    Toggles a user's active status (enabling/disabling account login).
    """
    if request.method == 'POST':
        user_to_toggle = get_object_or_404(User, pk=user_id)
        if user_to_toggle == request.user:
            messages.error(request, "You cannot deactivate your own administrative account.")
        else:
            user_to_toggle.is_active = not user_to_toggle.is_active
            user_to_toggle.save()
            status_text = "activated" if user_to_toggle.is_active else "suspended"
            messages.success(request, f"User account {user_to_toggle.email} has been successfully {status_text}.")
    return redirect('admin_dashboard')

@user_passes_test(is_admin, login_url='login')
def toggle_user_staff(request, user_id):
    """
    Toggles a user's staff status (granting/revoking admin panel rights).
    """
    if request.method == 'POST':
        user_to_toggle = get_object_or_404(User, pk=user_id)
        if user_to_toggle == request.user:
            messages.error(request, "You cannot revoke your own staff status.")
        else:
            user_to_toggle.is_staff = not user_to_toggle.is_staff
            user_to_toggle.save()
            status_text = "promoted to Staff" if user_to_toggle.is_staff else "demoted to Candidate"
            messages.success(request, f"User {user_to_toggle.email} has been {status_text}.")
    return redirect('admin_dashboard')
