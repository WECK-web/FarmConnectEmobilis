
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Listing, Category, Profile
from datetime import date

def verify_visibility():
    print("--- Verifying Marketplace Visibility for Farmers ---")
    
    # 1. Setup Data
    # Create Category
    cat, _ = Category.objects.get_or_create(name='TestCat')
    
    # Create Farmer A (Viewer)
    farmer_a_user, _ = User.objects.get_or_create(username='farmer_a', email='fa@test.com')
    farmer_a_user.set_password('pass123')
    farmer_a_user.save()
    Profile.objects.update_or_create(user=farmer_a_user, defaults={'user_type': 'FARMER'})
    
    # Create Farmer B (Seller)
    farmer_b_user, _ = User.objects.get_or_create(username='farmer_b', email='fb@test.com')
    Profile.objects.update_or_create(user=farmer_b_user, defaults={'user_type': 'FARMER'})
    
    # Create Listing by Farmer B
    Listing.objects.create(
        seller=farmer_b_user,
        title='Farmer B Product',
        description='Test',
        price=100,
        quantity=10,
        unit='kg',
        category=cat,
        expiry_date=date(2025, 12, 31),
        is_available=True
    )
    
    # 2. Login as Farmer A
    c = Client()
    login_success = c.login(username='farmer_a', password='pass123')
    if not login_success:
        print("❌ Login failed for Farmer A")
        return

    # 3. Check Home Page
    response = c.get('/')
    content = response.content.decode()
    
    if 'Farmer B Product' in content:
        print("✅ SUCCESS: Farmer A can see 'Farmer B Product'")
    else:
        print("❌ FAILURE: Farmer A CANNOT see 'Farmer B Product'")
        # print(content) # Debug if needed

if __name__ == '__main__':
    try:
        verify_visibility()
    except Exception as e:
        print(f"❌ Error: {e}")
