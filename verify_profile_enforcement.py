import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing

def verify_profile_enforcement():
    print("\n--- Verifying Profile Completeness Enforcement ---")
    client = Client()

    print("1. Setup User with Incomplete Profile")
    User.objects.filter(username='incomplete_user').delete()
    User.objects.filter(username='seller_enf').delete()
    user, _ = User.objects.get_or_create(username='incomplete_user', email='inc@test.com')
    user.set_password('pass123')
    user.save()
    # Ensure profile exists but has no phone/location
    user.profile.phone = ''
    user.profile.location = ''
    user.profile.save()

    client.force_login(user)
    
    # 2. Try to Access Restricted Action (e.g. Add to Cart)
    # Need a listing first
    seller = User.objects.create_user(username='seller_enf', password='password')
    listing = Listing.objects.create(seller=seller, title='Enforce Item', price=10, quantity=5, expiry_date='2025-12-31')

    print("[TEST] Add to Cart with Incomplete Profile")
    resp = client.post(reverse('cart_add', args=[listing.id]), follow=True)
    
    # Check if redirected to Profile Edit
    final_url = resp.request['PATH_INFO']
    if 'profile/edit' in final_url or 'profile' in final_url: # Adjust matching based on actual URL
        print(f"✅ SUCCESS: Redirected to Profile/Edit page ({final_url})")
        # Check for message?
    else:
        print(f"❌ FAILURE: Not redirected to profile. Landed on: {final_url}")

    # 3. Create Listing with Incomplete Profile (if user is farmer)
    user.profile.user_type = 'FARMER'
    user.profile.save()
    
    print("[TEST] Create Listing with Incomplete Profile")
    resp = client.get(reverse('create_listing'), follow=True)
    final_url = resp.request['PATH_INFO']
    
    if 'profile/edit' in final_url or 'profile' in final_url:
        print(f"✅ SUCCESS: Redirected to Profile/Edit page ({final_url})")
    else:
        print(f"❌ FAILURE: Not redirected to profile. Landed on: {final_url}")

    # Cleanup
    user.delete()
    seller.delete()

if __name__ == '__main__':
    verify_profile_enforcement()
