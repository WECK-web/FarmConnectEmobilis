
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.forms import UserRegisterForm
from core.models import Profile

def test_registration():
    print("--- START REGISTRATION DEBUG ---")
    
    # 1. Simulate POST data
    data = {
        'username': 'DebugFarmer1',
        'email': 'debugfarmer1@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'FARMER'
    }
    
    print(f"Simulating registration with data: {data}")
    
    # 2. Initialize Form
    form = UserRegisterForm(data=data)
    
    if form.is_valid():
        print("Form is VALID.")
        try:
            # 3. Save User
            user = form.save()
            print(f"User created: {user.username} (ID: {user.id})")
            
            # 4. Check if Profile exists (Signal verification)
            try:
                profile = user.profile
                print(f"Profile found for user. Current user_type: {profile.user_type}")
            except Exception as e:
                print(f"CRITICAL ERROR: user.profile access failed: {e}")
                return

            # 5. Update User Type manually (like in views.py)
            user_type = form.cleaned_data.get('user_type')
            print(f"User Type from form: {user_type}")
            
            user.profile.user_type = user_type
            user.profile.save()
            print("Profile saved with new user_type.")
            
            # 6. Verify Final State
            updated_profile = Profile.objects.get(user=user)
            print(f"Final Profile user_type: {updated_profile.user_type}")
            
            if updated_profile.user_type == 'FARMER':
                print("SUCCESS: Registered as FARMER.")
            else:
                print("FAILURE: User type is not FARMER.")
                
            # Cleanup
            print("Cleaning up debug user...")
            user.delete()
            print("Debug user deleted.")
            
        except Exception as e:
            print(f"Exception during save process: {e}")
    else:
        print("Form is INVALID.")
        print("ERRORS:")
        for field, errors in form.errors.items():
            print(f"- {field}: {errors}")

if __name__ == "__main__":
    # Ensure clean state
    try:
        User.objects.get(username='DebugFarmer1').delete()
    except User.DoesNotExist:
        pass
        
    test_registration()
