
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import Profile
from core.forms import UserUpdateForm, ProfileUpdateForm
from core.views import profile

def test_profile_update():
    print("--- START PROFILE UPDATE DEBUG ---")
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(username='debug_user_profile')
        if created:
            user.email = 'debug@example.com'
            user.set_password('password123')
            user.save()
            # Ensure profile exists
            if not hasattr(user, 'profile'):
                 Profile.objects.create(user=user, user_type='FARMER')
        
        print(f"Testing with user: {user.username}")
        
        # Simulate Data
        u_data = {
            'email': 'updated_debug@example.com',
            'first_name': 'Debug',
            'last_name': 'Updater'
        }
        
        p_data = {
            'phone': '0712345678',
            'location': 'Debug City',
            'bio': 'This is a debug bio.',
            'latitude': -1.2,
            'longitude': 36.8
        }
        
        # Test Forms directly first
        u_form = UserUpdateForm(u_data, instance=user)
        p_form = ProfileUpdateForm(p_data, instance=user.profile)
        
        print(f"User Form Valid? {u_form.is_valid()}")
        if not u_form.is_valid():
            print(f"User Errors: {u_form.errors}")

        print(f"Profile Form Valid? {p_form.is_valid()}")
        if not p_form.is_valid():
             print(f"Profile Errors: {p_form.errors}")
             
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            print("SUCCESS: Forms saved via direct script.")
        else:
            print("FAILURE: Forms invalid in script.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")
    finally:
        # Cleanup usually good, but keeping user for manual check might be useful
        pass

if __name__ == "__main__":
    test_profile_update()
