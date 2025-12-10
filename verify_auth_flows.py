import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

def verify_login_flows():
    print("\n--- Verifying Detailed Login Flows ---")
    client = Client()
    
    # 1. Setup Data
    password = 'TestPass123!'
    
    # Farmer
    farmer, _ = User.objects.get_or_create(username='flow_farmer', email='f@flow.com')
    farmer.set_password(password)
    farmer.save()
    Profile.objects.update_or_create(user=farmer, defaults={'user_type': 'FARMER'})
    
    # Consumer
    consumer, _ = User.objects.get_or_create(username='flow_consumer', email='c@flow.com')
    consumer.set_password(password)
    consumer.save()
    Profile.objects.update_or_create(user=consumer, defaults={'user_type': 'CONSUMER'})

    # 2. Test Farmer Redirect (Should go to Dashboard)
    print("\n[TEST] Farmer Login Redirect")
    resp = client.post('/login/', {'username': 'flow_farmer', 'password': password}, follow=True)
    if resp.redirect_chain:
        final_url = resp.redirect_chain[-1][0]
        # Expect /dashboard/ (reverse 'farmer_dashboard')
        # Note: reverse('farmer_dashboard') might differ if I changed urls. Let's check logic.
        # Actually I should check if it ends with dashboard
        if 'dashboard' in final_url:
            print(f"✅ SUCCESS: Farmer redirected to Dashboard ({final_url})")
        else:
            print(f"❌ FAILURE: Farmer redirected to {final_url} (Expected Dashboard)")
    else:
        print(f"❌ FAILURE: No redirect after login.")

    client.logout()

    # 3. Test Consumer Redirect (Should go to Home)
    print("\n[TEST] Consumer Login Redirect")
    resp = client.post('/login/', {'username': 'flow_consumer', 'password': password}, follow=True)
    if resp.redirect_chain:
        final_url = resp.redirect_chain[-1][0]
        # Expect / (home)
        if final_url == '/':
            print(f"✅ SUCCESS: Consumer redirected to Home ({final_url})")
        else:
            print(f"❌ FAILURE: Consumer redirected to {final_url} (Expected Home)")
    else:
        print("❌ FAILURE: No redirect.")

    client.logout()

    # 4. Test Deep Link ('next' parameter)
    print("\n[TEST] Deep Link Redirect (e.g. ?next=/profile/)")
    # Simulate login with next param
    resp = client.post('/login/?next=/profile/', {'username': 'flow_consumer', 'password': password}, follow=True)
    if resp.redirect_chain:
        # Check chain for /profile/
        # Chain might be: /login/ -> /profile/ (302) -> /profile/ (200)
        found_profile = any('/profile/' in url for url, status in resp.redirect_chain)
        final_path = resp.request['PATH_INFO'] # verify where we landed
        
        if found_profile or '/profile/' in final_path:
             print(f"✅ SUCCESS: Redirected to 'next' target (/profile/)")
        else:
             print(f"❌ FAILURE: Did not land on /profile/. Landed on: {final_path}")
    else:
         print("❌ FAILURE: No redirect.")

    client.logout()

    # 5. Test Redirect Loop Prevention (next=/login/)
    print("\n[TEST] Loop Prevention (next=/login/)")
    resp = client.post('/login/?next=/login/', {'username': 'flow_consumer', 'password': password}, follow=True)
    # Should NOT go to /login/. Should go to Home (Consumer default)
    final_path = resp.request['PATH_INFO']
    if final_path == '/':
        print(f"✅ SUCCESS: Loop prevented. Redirected to Home instead of /login/")
    elif final_path == '/login/':
        print(f"❌ FAILURE: Stuck in loop! Redirected back to /login/")
    else:
        print(f"⚠️ NOTE: partial success? Redirected to {final_path} (Safe, but not Home)")

    # Cleanup
    farmer.delete()
    consumer.delete()

if __name__ == '__main__':
    verify_login_flows()
