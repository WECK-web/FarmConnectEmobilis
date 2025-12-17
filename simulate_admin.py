import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def simulate_admin():
    print("--- Simulating Admin Dashboard ---")
    
    # 1. Setup Superuser
    admin, _ = User.objects.get_or_create(username='admin_user', defaults={'is_superuser': True, 'is_staff': True})
    admin.set_password('pass')
    admin.save()
    
    user, _ = User.objects.get_or_create(username='normal_user', defaults={'is_superuser': False})
    user.set_password('pass')
    user.save()
    
    client = Client()
    
    # 2. Test Normal User Access (Should Fail/Redirect)
    print("\n[TEST 1] Normal User Access")
    client.force_login(user)
    resp = client.get('/portal/dashboard/')
    if resp.status_code == 302:
        print("✅ Normal user redirected (Access Denied)")
    else:
        print(f"❌ Normal user accessed dashboard! Status: {resp.status_code}")

    # 3. Test Admin Access (Should Succeed)
    print("\n[TEST 2] Admin Access")
    client.force_login(admin)
    resp = client.get('/portal/dashboard/')
    
    if resp.status_code == 200:
        print("✅ Admin accessed dashboard")
        content = resp.content.decode()
        if 'Administrator Dashboard' in content:
            print("✅ Dashboard Title Found")
        if 'Total Users' in content:
             print("✅ Stats Rendered")
    else:
        print(f"❌ Admin FAILED to access dashboard! Status: {resp.status_code}")
        
    # 4. Test Restriction (Cart Access)
    print("\n[TEST 3] Admin Cart Restrictions")
    resp = client.get('/cart/')
    if resp.status_code == 302:
         # Check if redirected to dashboard or followed (messages handled in view)
         if '/portal/dashboard' in resp.url or '/home' in resp.url: # We redirected to dashboard in cart_detail
            print("✅ Admin redirected from Cart (Access Denied)")
         else:
             print(f"⚠️ Admin redirected to: {resp.url}")
    else:
        print(f"❌ Admin accessed cart! Status: {resp.status_code}")

    print("\n--- Admin Simulation Complete ---")

if __name__ == '__main__':
    simulate_admin()
