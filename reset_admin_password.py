import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

User = get_user_model()

# Ensure admin exists with known password
username = 'admin'
password = 'admin123'
email = 'admin@example.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Updated existing admin user '{username}' with password '{password}'")
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created new admin user '{username}' with password '{password}'")

# Ensure demo user exists for banning
demo_user = 'demouser'
try:
    d_user = User.objects.get(username=demo_user)
    d_user.is_active = True # Reset to active
    d_user.save()
    print(f"Reset {demo_user} to active")
except User.DoesNotExist:
    User.objects.create_user(username=demo_user, password='password123')
    print(f"Created {demo_user}")
