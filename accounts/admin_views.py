from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from django.core.cache import cache
from decouple import config
from resumes.models import Resume
from ai_engine.models import ATSFeedback, AIActionLog
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
    Renders system statistics, system controls, API status, user accounts, and real-time AI action logs.
    """
    # 1. System Statistics
    total_users = User.objects.count()
    total_resumes = Resume.objects.count()
    total_scans = ATSFeedback.objects.count()
    total_ai_logs = AIActionLog.objects.count()

    # 2. API Configuration
    import os
    keys_to_check = [
        ('GEMINI_API_KEY', 'Default Key (Fallback)'),
        ('GEMINI_PARSER_API_KEY', 'Resume Parser Key'),
        ('GEMINI_ATS_API_KEY', 'ATS Scanner Key'),
        ('GEMINI_COACH_API_KEY', 'Career Coach Key'),
        ('GEMINI_INTERVIEW_API_KEY', 'Interview Prep Key'),
        ('GEMINI_GENERATOR_API_KEY', 'Resume Generator Key'),
    ]
    
    api_keys_status = []
    default_client = get_gemini_client()
    api_configured = default_client is not None
    
    gemini_key = os.environ.get('GEMINI_API_KEY') or config('GEMINI_API_KEY', default='')
    if gemini_key:
        masked_key = f"{gemini_key[:8]}...{gemini_key[-8:]}" if len(gemini_key) > 10 else "Configured (Invalid Format)"
    else:
        masked_key = "Not Configured"
        
    for key_name, display_name in keys_to_check:
        key_val = os.environ.get(key_name) or config(key_name, default='')
        if key_val:
            client = get_gemini_client(key_name)
            status = 'Online' if client is not None else 'Invalid Key'
            masked_val = f"{key_val[:8]}...{key_val[-4:]}" if len(key_val) > 10 else "Invalid Format"
        else:
            status = 'Not Configured'
            masked_val = 'Not Configured'
            
        api_keys_status.append({
            'key_name': key_name,
            'display_name': display_name,
            'masked_val': masked_val,
            'status': status
        })

    # 3. System Control Flags (stored in cache as simple toggles)
    maintenance_mode = cache.get('admin_maintenance_mode', False)
    api_logging      = cache.get('admin_api_logging', True)

    # 4. Handle System Controls POST
    if request.method == 'POST' and 'apply_system_changes' in request.POST:
        maintenance_mode = 'maintenance_mode' in request.POST
        api_logging      = 'api_logging' in request.POST
        cache.set('admin_maintenance_mode', maintenance_mode, timeout=None)
        cache.set('admin_api_logging', api_logging, timeout=None)
        messages.success(request, 'System settings updated successfully.')
        return redirect('admin_dashboard')

    # 5. Clear AI logs action
    if request.method == 'POST' and 'clear_logs' in request.POST:
        AIActionLog.objects.all().delete()
        messages.success(request, 'AI operation logs cleared.')
        return redirect('admin_dashboard')

    # 6. User accounts with resume count
    users = User.objects.annotate(resume_count=Count('resumes')).order_by('-date_joined')

    # 7. Recent AI Logs (latest 20)
    ai_logs = AIActionLog.objects.select_related().all()[:20]

    context = {
        'total_users':       total_users,
        'total_resumes':     total_resumes,
        'total_scans':       total_scans,
        'total_ai_logs':     total_ai_logs,
        'api_configured':    api_configured,
        'masked_key':        masked_key,
        'api_keys_status':   api_keys_status,
        'users_list':        users,
        'gemini_model':      'gemini-2.5-flash',
        'maintenance_mode':  maintenance_mode,
        'api_logging':       api_logging,
        'ai_logs':           ai_logs,
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

import os

@user_passes_test(is_admin, login_url='login')
def update_api_config(request):
    """
    Updates a specific Gemini API key inside the local .env file AND applies it
    immediately to the running process via os.environ so no restart is needed.
    """
    if request.method == 'POST':
        key_name = request.POST.get('key_name', 'GEMINI_API_KEY').strip()
        new_key = request.POST.get('api_key', '').strip()
        
        allowed_keys = [
            'GEMINI_API_KEY', 'GEMINI_PARSER_API_KEY', 'GEMINI_ATS_API_KEY',
            'GEMINI_COACH_API_KEY', 'GEMINI_INTERVIEW_API_KEY', 'GEMINI_GENERATOR_API_KEY',
            'GEMINI_REWRITER_API_KEY', 'GEMINI_COVER_LETTER_API_KEY', 'GEMINI_GRAMMAR_API_KEY'
        ]
        
        if key_name not in allowed_keys:
            messages.error(request, "Invalid API Key type.")
            return redirect('admin_dashboard')

        if not new_key:
            messages.error(request, "API Key cannot be empty.")
            return redirect('admin_dashboard')

        env_path = os.path.join(settings.BASE_DIR, '.env')
        lines = []
        updated = False

        # Read existing .env
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()

        # Replace or append target key line
        prefix = f"{key_name}="
        for i, line in enumerate(lines):
            if line.strip().startswith(prefix):
                lines[i] = f"{key_name}={new_key}\n"
                updated = True
                break

        if not updated:
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            lines.append(f"{key_name}={new_key}\n")

        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(lines)

        # ✅ Apply to running process immediately (no server restart needed)
        os.environ[key_name] = new_key

        messages.success(
            request,
            f"✅ {key_name} updated successfully! New key: {new_key[:8]}...{new_key[-4:]} is now active."
        )

    return redirect('admin_dashboard')
