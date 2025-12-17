
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

def verify_geolocation():
    print("Verifying Geolocation...")

    # 1. Setup Data
    if User.objects.filter(username='farmer_geo_test').exists():
        User.objects.get(username='farmer_geo_test').delete()

    farmer = User.objects.create_user(username='farmer_geo_test', password='password')
    farmer.profile.user_type = 'FARMER'
    # Set Nairobi Coordinates
    farmer.profile.latitude = -1.2921
    farmer.profile.longitude = 36.8219
    farmer.profile.location = "Nairobi, Kenya"
    farmer.profile.save()
    
    # 2. Check if farmer is returned in the query used by 'home' view
    farmers_with_location = User.objects.filter(
        profile__user_type='FARMER',
        profile__latitude__isnull=False,
        profile__longitude__isnull=False
    ).select_related('profile')
    
    if farmer in farmers_with_location:
        print("SUCCESS: Farmer with location found in query.")
        print(f"Coordinates: {farmer.profile.latitude}, {farmer.profile.longitude}")
    else:
        print("FAILURE: Farmer with location NOT found in query.")

    # Cleanup (Optional, keep for browser verification if needed)
    # User.objects.get(username='farmer_geo_test').delete()

if __name__ == '__main__':
    verify_geolocation()
