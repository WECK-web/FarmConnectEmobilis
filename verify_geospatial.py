import os
import django
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile
from django.test import Client, RequestFactory
from core.views import nearby_farmers
from decimal import Decimal

def verify_geospatial():
    print("--- Verifying Geospatial Search ---")
    
    # 1. Setup Data: 2 Farmers
    # User at (0, 0)
    # Farmer A at (0.1, 0.1) approx 15km away
    # Farmer B at (1.0, 1.0) approx 157km away
    
    f1, _ = User.objects.get_or_create(username='geo_farmer_near')
    Profile.objects.update_or_create(user=f1, defaults={
        'user_type': 'FARMER',
        'latitude': Decimal('0.1'),
        'longitude': Decimal('0.1'),
        'location': 'Near Town'
    })

    f2, _ = User.objects.get_or_create(username='geo_farmer_far')
    Profile.objects.update_or_create(user=f2, defaults={
        'user_type': 'FARMER',
        'latitude': Decimal('1.0'),
        'longitude': Decimal('1.0'),
        'location': 'Far City'
    })
    
    client = Client()
    
    # Test 1: Radius 50km (Should find Farmer A only)
    print("\n[TEST 1] Radius 50km (Expect: Farmer Near)")
    resp = client.get('/farmers/nearby/', {'lat': '0', 'lon': '0', 'radius': '50'})
    content = resp.content.decode()
    
    if 'geo_farmer_near' in content:
        print("✅ Correctly found 'geo_farmer_near'")
    else:
        print("❌ FAILED to find 'geo_farmer_near'")
        
    if 'geo_farmer_far' not in content:
        print("✅ Correctly excluded 'geo_farmer_far'")
    else:
        print("❌ FAILED to exclude 'geo_farmer_far'")

    # Test 2: Radius 200km (Should find Both)
    print("\n[TEST 2] Radius 200km (Expect: Both)")
    resp = client.get('/farmers/nearby/', {'lat': '0', 'lon': '0', 'radius': '200'})
    content = resp.content.decode()
    
    if 'geo_farmer_near' in content and 'geo_farmer_far' in content:
        print("✅ Correctly found both farmers")
    else:
        print("❌ FAILED to find both farmers")
        
    print("\n--- Geospatial Verification Complete ---")

if __name__ == '__main__':
    verify_geospatial()
