import os
import django
from django.test import Client, RequestFactory
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Order, Profile

def reproduce_status_issue():
    print("--- Reproducing Order Status Issue ---")
    client = Client()
    
    # Create Users
    farmer, _ = User.objects.get_or_create(username='status_farmer', email='sf@t.com')
    farmer.set_password('pass')
    farmer.save()
    Profile.objects.update_or_create(user=farmer, defaults={'user_type': 'FARMER'})
    
    buyer, _ = User.objects.get_or_create(username='status_buyer', email='sb@t.com')
    buyer.set_password('pass')
    buyer.save()
    Profile.objects.update_or_create(user=buyer, defaults={'user_type': 'CONSUMER'})
    
    # Create Listing and Order
    listing = Listing.objects.create(seller=farmer, title="Status Test Item", price=10, quantity=5, expiry_date='2025-12-31')
    order = Order.objects.create(listing=listing, buyer=buyer, quantity=1, status='PENDING')
    
    print(f"Created Order #{order.id} with status: {order.status}")
    
    # Login as Farmer
    client.force_login(farmer)
    
    # Test GET (Load Form)
    print("\n[TEST] Accessing Update Page (GET)...")
    try:
        url = reverse('update_order_status', args=[order.id])
        resp = client.get(url)
        if resp.status_code == 200:
            print("[SUCCESS] Update page loaded.")
        else:
            print(f"[FAILURE] Update page failed. Status: {resp.status_code}")
    except Exception as e:
        print(f"[FAILURE] Exception on GET: {e}")
        
    # Test POST (Submit Form)
    print("\n[TEST] Submitting Update (POST)...")
    try:
        resp = client.post(url, {
            'status': 'SHIPPED',
            'tracking_notes': 'Valid update',
            'estimated_delivery': '2025-12-31'
        }, follow=True)
        
        if resp.status_code == 200:
            order.refresh_from_db()
            if order.status == 'SHIPPED':
                print(f"[SUCCESS] Order status updated to: {order.status}")
            else:
                print(f"[FAILURE] Order status did NOT update. Current: {order.status}")
        else:
            print(f"[FAILURE] POST request failed. Status: {resp.status_code}")
            
    except Exception as e:
        print(f"[FAILURE] Exception on POST: {e}")

if __name__ == '__main__':
    reproduce_status_issue()
