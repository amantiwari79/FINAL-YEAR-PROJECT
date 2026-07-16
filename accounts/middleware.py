from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout

class MaintenanceModeMiddleware:
    """
    Middleware to intercept requests when maintenance mode is active.
    If maintenance mode is active:
    - Admins and staff users are allowed full access.
    - Regular users are logged out and redirected to login/landing with a message.
    - Non-logged in users trying to access protected paths are redirected.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check if maintenance mode is enabled in cache
        if cache.get('admin_maintenance_mode', False):
            # Admin and staff users are allowed bypass
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                return self.get_response(request)

            path = request.path
            
            # Exact matches for allowed paths
            exact_allowed = [
                reverse('landing'),
                reverse('login'),
                reverse('logout'),
                reverse('privacy_policy'),
                reverse('terms_conditions'),
                reverse('contact_support'),
                reverse('about'),
                reverse('features'),
            ]
            
            # Prefix matches for allowed paths
            prefix_allowed = [
                '/admin/',
                '/admin-panel/',
                '/static/',
                '/media/',
            ]
            
            # Check if path is in exact matches or starts with prefix matches
            is_allowed = (path in exact_allowed) or any(path.startswith(pref) for pref in prefix_allowed)
            
            if not is_allowed:
                if request.user.is_authenticated:
                    logout(request)
                messages.error(request, 'Website is under maintenance. Please try again later.')
                return redirect('login')

        return self.get_response(request)
