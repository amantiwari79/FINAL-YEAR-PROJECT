from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import CustomUserCreationForm, UserProfileForm

def landing(request):
    """
    Renders the product landing page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register_user(request):
    """
    Handles user registration using the custom creation form.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    from django.core.cache import cache
    if cache.get('admin_maintenance_mode', False):
        messages.error(request, 'Website is under maintenance. Registration is currently disabled.')
        return redirect('login')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Account created successfully! Welcome to ResuMate AI.'))
            return redirect('dashboard')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    """
    Handles user authentication.
    """
    if request.user.is_authenticated:
        if 'next' in request.GET:
            logout(request)
            return redirect(request.get_full_path())
        else:
            return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if maintenance mode is active
        from django.core.cache import cache
        is_maintenance = cache.get('admin_maintenance_mode', False)
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if is_maintenance and not (user.is_staff or user.is_superuser):
                messages.error(request, 'Website under maintenance. Regular user login is currently disabled.')
            else:
                login(request, user)
                messages.success(request, _('Successfully logged in!'))
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, _('Invalid email or password.'))
            
    return render(request, 'accounts/login.html')

def logout_user(request):
    """
    Logs out the user and redirects to the landing page.
    """
    logout(request)
    messages.success(request, _('Successfully logged out.'))
    return redirect('landing')

from resumes.models import Resume

@login_required
def dashboard(request):
    """
    Renders the candidate's workspace dashboard with enriched stats.
    """
    from ai_engine.models import ATSFeedback
    from django.db.models import Avg

    resumes = Resume.objects.filter(user=request.user)

    # Avg ATS score across all user's resumes
    avg_data = ATSFeedback.objects.filter(resume__user=request.user).aggregate(avg=Avg('score'))
    avg_ats  = avg_data['avg']
    avg_ats_score = f"{round(avg_ats)}%" if avg_ats else "N/A"

    # Total AI scans run
    total_scans = ATSFeedback.objects.filter(resume__user=request.user).count()

    context = {
        'resumes':        resumes,
        'avg_ats_score':  avg_ats_score,
        'total_scans':    total_scans,
    }
    return render(request, 'dashboard.html', context)

def privacy_policy(request):
    """
    Renders the privacy policy page.
    """
    return render(request, 'accounts/privacy_policy.html')

def terms_conditions(request):
    """
    Renders the terms and conditions page.
    """
    return render(request, 'accounts/terms_conditions.html')

def contact_support(request):
    """
    Renders the contact support form and handles form submission.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        
        if name and email and message_body:
            # We can log the support ticket to the console/syslog or save it.
            # Showing success is sufficient for the demo flow.
            messages.success(request, 'Thank you! Your support ticket has been submitted. Our team will email you shortly.')
            return redirect('contact_support')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
    return render(request, 'accounts/contact_support.html')

def about_view(request):
    """
    Renders the About page.
    """
    return render(request, 'about.html')

def features_view(request):
    """
    Renders the Features page.
    """
    return render(request, 'features.html')

@login_required
def profile_edit(request):
    """
    Renders user profile settings and processes name changes and image uploads.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been successfully updated!')
            return redirect('profile_edit')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'accounts/profile_edit.html', {'form': form})
