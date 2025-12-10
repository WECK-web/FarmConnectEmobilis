import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User

def verify_redirect():
    print("--- Verifying Login Redirect Logic ---")
    client = Client()
    
    # Create test user
    username = 'redirect_test_user'
    password = 'TestPass123!'
    try:
        user = User.objects.create_user(username=username, password=password)
        # Give profile (default Consumer)
        user.profile.user_type = 'CONSUMER'
        user.profile.save()
    except Exception as e:
        print(f"Using existing user: {e}")
        user = User.objects.get(username=username)

    # Test 1: Forced Redirect (next parameter)
    # Simulate user trying to access /checkout/ without login
    # Login url should be /login/?next=/checkout/
    
    print("Testing 'next' parameter redirection...")
    resp = client.post(f'/login/?next=/checkout/', {
        'username': username,
        'password': password
    }, follow=True) # follow redirects
    
    # Check if we landed on /checkout/ (or whatever checkout renders)
    # Note: checkout might redirect if cart empty, but we check if we were sent there first
    
    chain = resp.redirect_chain
    if chain:
        print(f"Redirect chain: {chain}")
        # Look for /checkout/ in the chain
        if any('/checkout/' in url for url, status in chain):
            print("SUCCESS: Redirected to 'next' URL.")
        else:
            print(f"FAILURE: Did not redirect to 'next'. Landed at: {chain[-1][0]}")
    else:
        print("FAILURE: No redirect occurred.")

    # Cleanup
    user.delete()

if __name__ == '__main__':
    verify_redirect()
