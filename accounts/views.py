from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import CustomUserCreationForm

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
        else:
            return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
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
    Renders the candidate's workspace dashboard.
    """
    resumes = Resume.objects.filter(user=request.user)
    context = {
        'resumes': resumes
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
