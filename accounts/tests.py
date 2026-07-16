from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class MaintenanceModeTests(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        self.normal_user_email = 'user@example.com'
        self.normal_user_password = 'password123'
        self.normal_user = User.objects.create_user(
            email=self.normal_user_email,
            password=self.normal_user_password,
            first_name='John',
            last_name='Doe'
        )
        
        self.admin_user_email = 'admin@example.com'
        self.admin_user_password = 'adminpassword'
        self.admin_user = User.objects.create_superuser(
            email=self.admin_user_email,
            password=self.admin_user_password,
            first_name='Admin',
            last_name='User'
        )

    def tearDown(self):
        cache.clear()

    def test_normal_operations_when_maintenance_inactive(self):
        # 1. Normal user login should succeed
        response = self.client.post(reverse('login'), {
            'email': self.normal_user_email,
            'password': self.normal_user_password
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_blocked_for_normal_user_when_maintenance_active(self):
        # Activate maintenance mode
        cache.set('admin_maintenance_mode', True, timeout=None)

        # Normal user login should fail
        response = self.client.post(reverse('login'), {
            'email': self.normal_user_email,
            'password': self.normal_user_password
        })
        self.assertEqual(response.status_code, 200) # Re-renders login page
        # Check that error message is present
        messages = list(response.context['messages'])
        self.assertTrue(any('Website under maintenance' in str(m) for m in messages))

    def test_login_allowed_for_admin_when_maintenance_active(self):
        # Activate maintenance mode
        cache.set('admin_maintenance_mode', True, timeout=None)

        # Admin user login should succeed
        response = self.client.post(reverse('login'), {
            'email': self.admin_user_email,
            'password': self.admin_user_password
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_registration_blocked_when_maintenance_active(self):
        # Activate maintenance mode
        cache.set('admin_maintenance_mode', True, timeout=None)

        # Accessing register page should redirect to login
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('login'))

        # Posting registration should also redirect/block
        response = self.client.post(reverse('register'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        self.assertRedirects(response, reverse('login'))

    def test_logged_in_user_redirected_when_maintenance_activated(self):
        # Login first while inactive
        self.client.force_login(self.normal_user)
        
        # Verify dashboard is accessible
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Activate maintenance mode
        cache.set('admin_maintenance_mode', True, timeout=None)

        # Try to access dashboard again - should logout and redirect to login
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))
        
        # Check user is logged out (session does not contain _auth_user_id)
        self.assertNotIn('_auth_user_id', self.client.session)
