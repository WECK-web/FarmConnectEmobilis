import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

def verify_verification():
    print("--- Verifying Farmer Verification Logic ---")
    
    # 1. Setup
    admin, _ = User.objects.get_or_create(username='admin_check', defaults={'is_superuser': True, 'is_staff': True})
    admin.set_password('pass')
    admin.save()
    
    farmer_user, _ = User.objects.get_or_create(username='farmer_to_verify')
    farmer_profile, _ = Profile.objects.update_or_create(user=farmer_user, defaults={'user_type': 'FARMER', 'is_verified': False})
    
    client = Client()
    client.force_login(admin)
    
    # 2. Verify Initial State
    print(f"Initial Status: {farmer_user.profile.is_verified}")
    if not farmer_user.profile.is_verified:
        print("✅ Correctly initialized as Unverified")
        
    # 3. Toggle ON
    print("\n[TEST 1] Toggle ON")
    resp = client.get(f'/portal/users/verify/{farmer_user.id}/', follow=True)
    
    farmer_user.refresh_from_db()
    if farmer_user.profile.is_verified:
        print(f"✅ Farmer is now VERIFIED.")
    else:
        print("❌ Toggle ON Failed")
        
    # 4. Toggle OFF
    print("\n[TEST 2] Toggle OFF")
    client.get(f'/portal/users/verify/{farmer_user.id}/', follow=True)
    
    farmer_user.refresh_from_db()
    if not farmer_user.profile.is_verified:
        print("✅ Farmer is now UNVERIFIED")
    else:
        print("❌ Toggle OFF Failed")

    print("\n--- Verification Complete ---")

if __name__ == '__main__':
    verify_verification()
