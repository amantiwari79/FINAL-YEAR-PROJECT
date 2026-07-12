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
