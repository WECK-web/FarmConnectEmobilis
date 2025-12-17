
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

username = 'farmer_test'
password = 'farmer123'
email = 'farmer@test.com'

try:
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists. Resetting password.")
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
    else:
        print(f"Creating user {username}.")
        u = User.objects.create_user(username, email, password)
    
    # Ensure profile exists and is FARMER
    p, created = Profile.objects.get_or_create(user=u)
    p.user_type = 'FARMER'
    p.is_verified = True  # Verified farmer
    p.save()
    print("Farmer setup complete.")

except Exception as e:
    print(f"Error: {e}")
