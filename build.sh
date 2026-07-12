#!/usr/bin/env bash
# Render.com deployment startup script
# This runs BEFORE the web server starts on every deploy

set -e  # Exit on any error

echo "=== Starting Render Deploy Script ==="

# Step 1: Run database migrations
echo ">>> Running migrations..."
python manage.py migrate --no-input

# Step 2: Collect static files
echo ">>> Collecting static files..."
python manage.py collectstatic --no-input

# Step 3: Seed admin accounts (creates them if missing, updates password if present)
echo ">>> Seeding admin accounts..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

admin_accounts = [
    'admin@123gmail.com',
    'admin123@gmail.com',
    'admin@gmail.com',
]

for email in admin_accounts:
    user, created = User.objects.update_or_create(
        email=email,
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'first_name': 'System',
            'last_name': 'Admin',
        }
    )
    user.set_password('admin@123')
    user.save()
    status = 'created' if created else 'updated'
    print(f'Admin account {email} {status} successfully.')

print('All admin accounts seeded!')
"

echo "=== Deploy Script Complete ==="
