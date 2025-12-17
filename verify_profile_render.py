
import os
import django
from django.template.loader import render_to_string

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.forms import ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User

def test_render():
    print("--- START PROFILE RENDERING TEST ---")
    try:
        # Mock Request/User
        class MockUser:
            username = "TestFarmer"
            email = "farmer@test.com"
            is_superuser = False
            class Profile:
                user_type = "FARMER"
                get_user_type_display = "Farmer"
                avatar = None
            profile = Profile()

        u_form = UserUpdateForm()
        p_form = ProfileUpdateForm()
        
        context = {
            'user': MockUser(),
            'u_form': u_form,
            'p_form': p_form
        }
        
        rendered = render_to_string('profile.html', context)
        
        # Check for HARDCODED labels
        print("--- VALIDATION CHECK ---")
        if "{{ p_form.avatar.label }}" in rendered:
            print("FAILURE: Found literal '{{ p_form.avatar.label }}' in output!")
        elif "Profile Picture" in rendered and "Phone Number" in rendered:
             print("SUCCESS: Found hardcoded 'Profile Picture' and 'Phone Number' labels.")
        else:
            print("WARNING: Inconclusive. Dumping relevant lines:")
            
        print("--- SNIPPET ---")
        lines = rendered.split('\n')
        for i, line in enumerate(lines):
            if "Profile Picture" in line or "Phone Number" in line:
                print(f"{i}: {line.strip()}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_render()
