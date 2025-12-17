import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Wishlist, Profile
from django.test import Client

def simulate_wishlist():
    print("--- Simulating Wishlist ---")
    
    # 1. Setup
    u, _ = User.objects.get_or_create(username='wishlist_user')
    u.set_password('pass')
    u.save()
    Profile.objects.update_or_create(user=u, defaults={'user_type': 'CONSUMER'})
    
    seller, _ = User.objects.get_or_create(username='wishlist_seller')
    Profile.objects.update_or_create(user=seller, defaults={'user_type': 'FARMER'})
    
    l, _ = Listing.objects.get_or_create(seller=seller, title='Wish Item', defaults={'price': 100, 'quantity': 10, 'expiry_date': '2025-12-31'})
    
    # Clear existing
    Wishlist.objects.filter(user=u).delete()
    
    client = Client()
    client.force_login(u)
    
    # 2. Toggle ON
    print("\n[TEST 1] Toggle ON")
    resp = client.get(f'/wishlist/toggle/{l.id}/')
    data = resp.json()
    
    if data['added'] == True:
        print("✅ API returned added=True")
    else:
        print(f"❌ API Failed: {data}")
        
    if Wishlist.objects.filter(user=u, listing=l).exists():
        print("✅ Wishlist DB entry created")
    else:
        print("❌ Wishlist DB entry MISSING")

    # 3. Verify Wishlist View
    print("\n[TEST 2] Wishlist Page")
    try:
        resp = client.get('/wishlist/')
        content = resp.content.decode()
        
        if 'Wish Item' in content:
            print("✅ Wishlist page contains item")
        else:
             print("❌ Wishlist page MISSING item")
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")
        import traceback
        with open('error_log.txt', 'w') as f:
            traceback.print_exc(file=f)
            f.write(str(e))

    # 4. Toggle OFF
    print("\n[TEST 3] Toggle OFF")
    resp = client.get(f'/wishlist/toggle/{l.id}/')
    data = resp.json()
    
    if data['added'] == False:
        print("✅ API returned added=False")
    else:
        print(f"❌ API Failed: {data}")
        
    if not Wishlist.objects.filter(user=u, listing=l).exists():
        print("✅ Wishlist DB entry deleted")
    else:
        print("❌ Wishlist DB entry STILL EXISTS")

    print("\n--- Wishlist Simulation Complete ---")

if __name__ == '__main__':
    simulate_wishlist()
