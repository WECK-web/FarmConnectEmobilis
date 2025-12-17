
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

username = 'admin_test'
password = 'admin123'
email = 'admin@test.com'

try:
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists. Resetting password.")
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_staff = True
        u.is_superuser = True
        u.save()
    else:
        print(f"Creating user {username}.")
        u = User.objects.create_superuser(username, email, password)
    
    # Ensure profile exists
    Profile.objects.get_or_create(user=u, user_type='FARMER')
    print("Superuser setup complete.")

except Exception as e:
    print(f"Error: {e}")
