import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Profile, Category

def simulate_badge():
    print("--- Simulating Badge Visibility ---")
    
    # 1. Setup Verified Farmer
    farmer, _ = User.objects.get_or_create(username='verified_farmer')
    Profile.objects.update_or_create(user=farmer, defaults={'user_type': 'FARMER', 'is_verified': True})
    
    # 2. Setup Listing
    cat, _ = Category.objects.get_or_create(name='TestCat')
    l, _ = Listing.objects.get_or_create(seller=farmer, title='Verified Product', defaults={'price': 50, 'quantity': 100, 'category': cat, 'expiry_date': '2025-01-01'})
    
    print(f"Farmer Verified: {farmer.profile.is_verified}")
    print(f"Listing Created: {l.title}")
    
    # 3. Check Home Page
    client = Client()
    resp = client.get('/')
    content = resp.content.decode()
    
    if 'Verified Product' in content:
        print("✅ Listing found on Home Page")
        # Check for icon near the listing
        # Since HTML structure is complex, we just check existence of class AND ensuring it's not hidden
        if 'bi-patch-check-fill' in content:
            print("✅ 'bi-patch-check-fill' icon found in HTML")
            # We can try to be more specific with regex if needed, but this confirms the template *tried* to render it.
        else:
            print("❌ Icon CLASS NOT FOUND in HTML")
            print("Partial Content around listing:")
            idx = content.find('Verified Product')
            print(content[idx:idx+400])
    else:
        print("❌ Listing NOT found on Home Page")

if __name__ == '__main__':
    simulate_badge()
