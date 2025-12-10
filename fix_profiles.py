import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

def fix_profiles():
    print("Checking for users without profiles...")
    users = User.objects.all()
    count = 0
    for user in users:
        if not hasattr(user, 'profile'):
            print(f"Creating profile for user: {user.username}")
            # Default to CONSUMER if unknown, or SUPERUSER/FARMER if admin? 
            # safe default is CONSUMER
            Profile.objects.create(user=user, user_type='CONSUMER')
            count += 1
    
    if count == 0:
        print("All users already have profiles.")
    else:
        print(f"Created {count} missing profiles.")

if __name__ == '__main__':
    fix_profiles()
