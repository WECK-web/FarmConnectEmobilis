import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ActivityLog

def verify_admin_nav():
    print("--- Verifying Admin Navigation & Features ---")
    
    # 1. Setup Support Check
    admin, _ = User.objects.get_or_create(username='nav_admin', defaults={'is_superuser': True, 'is_staff': True})
    consumer, _ = User.objects.get_or_create(username='nav_consumer', defaults={'is_superuser': False})
    
    client = Client()
    client.force_login(admin)
    
    # 2. Check Admin View (Should NOT see wishlist/cart/orders, SHOULD see Logs)
    print("Checking Admin View...")
    resp = client.get('/')
    content = resp.content.decode()
    
    if 'wishlist' in content and 'Wishlist' in content: 
        # Note: 'wishlist' might be in URL, we check visual text "Wishlist" or link presence
        # Actually my change hides the link block.
        if 'bi-heart-fill' in content:
            print("❌ Admin CAN see Wishlist (Failed)")
        else:
            print("✅ Admin CANNOT see Wishlist")
    else:
        print("✅ Admin CANNOT see Wishlist")
        
    if 'activity_logs' in content:
        print("✅ Admin CAN see Activity Logs link")
    else:
        print("❌ Admin CANNOT see Activity Logs link")
        
    # 3. Check Activity Logs Page
    ActivityLog.objects.create(user=admin, content="Test Action")
    resp = client.get('/portal/logs/')
    if resp.status_code == 200:
        print("✅ Activity Logs page accessed successfully")
        if "Test Action" in resp.content.decode():
             print("✅ Log entry found")
    else:
        print(f"❌ Failed to access Activity Logs (Status: {resp.status_code})")

    # 4. Check Consumer View (Should see Wishlist, NOT Logs)
    client.force_login(consumer)
    print("\nChecking Consumer View...")
    resp = client.get('/')
    content = resp.content.decode()
    
    if 'bi-heart-fill' in content:
        print("✅ Consumer CAN see Wishlist")
    else:
        print("❌ Consumer CANNOT see Wishlist")
        
    if 'activity_logs' in content:
        print("❌ Consumer CAN see Activity Logs link")
    else:
        print("✅ Consumer CANNOT see Activity Logs link")

if __name__ == '__main__':
    verify_admin_nav()
