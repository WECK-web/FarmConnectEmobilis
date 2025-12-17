import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Profile, Category

def verify_management():
    print("--- Verifying Admin Management UI ---")
    
    # Setup
    admin, _ = User.objects.get_or_create(username='admin_boss', defaults={'is_superuser': True, 'is_staff': True})
    admin.set_password('pass')
    admin.save()
    
    target_user, _ = User.objects.get_or_create(username='user_to_delete')
    target_user.set_password('pass')
    target_user.save()
    
    target_listing = Listing.objects.create(seller=admin, title="Listing to Delete", price=10, quantity=1, expiry_date='2030-01-01')

    client = Client()
    client.force_login(admin)
    
    # 1. Access Manage Users
    print("\n[TEST 1] Access Manage Users")
    resp = client.get('/portal/users/')
    if resp.status_code == 200 and 'Manage Users' in resp.content.decode():
        print("✅ Manage Users Page OK")
    else:
        print(f"❌ Manage Users Page Failed: {resp.status_code}")

    # 2. Delete User
    print("\n[TEST 2] Delete User")
    resp = client.get(f'/portal/users/delete/{target_user.id}/', follow=True)
    if not User.objects.filter(id=target_user.id).exists():
        print("✅ User Deleted Successfully")
    else:
        print("❌ User Deletion Failed")

    # 3. Access Manage Listings
    print("\n[TEST 3] Access Manage Listings")
    resp = client.get('/portal/listings/')
    if resp.status_code == 200 and 'Manage Listings' in resp.content.decode():
        print("✅ Manage Listings Page OK")

    # 4. Delete Listing
    print("\n[TEST 4] Delete Listing")
    listing_id = target_listing.id
    resp = client.get(f'/portal/listings/delete/{listing_id}/', follow=True) # Assuming GET for simplicity in view implementation
    if not Listing.objects.filter(id=listing_id).exists():
        print("✅ Listing Deleted Successfully")
    else:
        print("❌ Listing Deletion Failed")

    # 5. Access Manage Orders
    print("\n[TEST 5] Manage Orders")
    resp = client.get('/portal/orders/')
    if resp.status_code == 200:
        print("✅ Manage Orders Page OK")
        
    # 6. Manage Categories
    print("\n[TEST 6] Manage Categories")
    resp = client.get('/portal/categories/')
    if resp.status_code == 200:
        print("✅ Manage Categories Page OK")
        
    # 7. Create Category
    print("\n[TEST 7] Create Category")
    resp = client.post('/portal/categories/', {'name': 'New Test Cat'})
    if resp.status_code == 302 and Category.objects.filter(name='New Test Cat').exists():
         print("✅ Category Created Successfully")
    else:
         print(f"❌ Category Creation Failed: {resp.status_code}")

    print("\n--- Verification Complete ---")

if __name__ == '__main__':
    verify_management()
