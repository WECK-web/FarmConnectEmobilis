
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Profile

def test_view_submission():
    print("--- TESTING PROFILE VIEW SUBMISSION ---")
    
    # Setup User
    username = 'view_test_user'
    password = 'password123'
    email = 'viewtest@example.com'
    
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.delete() # Clean slate
        
    user = User.objects.create_user(username=username, email=email, password=password)
    # Profile auto-created by signal?
    if not hasattr(user, 'profile'):
         Profile.objects.create(user=user, user_type='FARMER')
    
    c = Client()
    login_success = c.login(username=username, password=password)
    print(f"Login Success: {login_success}")
    
    url = reverse('profile')
    print(f"Posting to: {url}")
    
    data = {
        'first_name': 'View',
        'last_name': 'Tester',
        'email': email,
        'phone': '0700000000',
        'location': 'Test Location',
        'bio': 'Test Bio',
        'latitude': -1.5,
        'longitude': 37.0
    }
    
    response = c.post(url, data)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 302:
        print("Redirect detected (Likely Success -> /profile/)")
        user.refresh_from_db()
        print(f"Updated Name: {user.first_name}")
        print(f"Updated Phone: {user.profile.phone}")
        if user.first_name == 'View' and user.profile.phone == '0700000000':
             print("SUCCESS: View updated profile correctly.")
        else:
             print("FAILURE: Redirected but data mismatch.")
    else:
        print("FAILURE: Did not redirect. Form likely invalid.")
        # Try to find errors in context
        if 'p_form' in response.context:
             print(f"Profile Errors: {response.context['p_form'].errors}")
        if 'u_form' in response.context:
             print(f"User Errors: {response.context['u_form'].errors}")

if __name__ == "__main__":
    test_view_submission()
