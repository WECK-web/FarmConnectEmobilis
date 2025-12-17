
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Listing, Category, Profile, Order
from datetime import date
from decimal import Decimal

def verify_farmer_journey():
    print("\n--- Verifying Farmer Experience (Preview) ---")
    c = Client()
    
    # 1. Setup Wrapper
    print("\n[STEP 1] Data Setup")
    cat, _ = Category.objects.get_or_create(name='Valid Vegetables')
    
    import random
    suffix = random.randint(1000, 9999)
    farmer_username = f'farmer_preview_{suffix}'
    buyer_username = f'buyer_preview_{suffix}'
    
    # Create Farmer User
    farmer_user, _ = User.objects.get_or_create(username=farmer_username, email=f'fp{suffix}@test.com')
    farmer_user.set_password('pass123')
    farmer_user.save()
    Profile.objects.update_or_create(
        user=farmer_user, 
        defaults={
            'user_type': 'FARMER',
            'phone_number': '0700000000',
            'location': 'Nairobi',
            'latitude': -1.2,
            'longitude': 36.8
        }
    )
    print("✅ Farmer User 'farmer_preview' ready.")

    # Create Buyer User for ordering
    buyer_user, _ = User.objects.get_or_create(username=buyer_username, email=f'bp{suffix}@test.com')
    buyer_user.set_password('pass123')
    buyer_user.save()
    Profile.objects.update_or_create(user=buyer_user, defaults={'user_type': 'CONSUMER'})

    # 2. Login
    print("\n[STEP 2] Farmer Login")
    login_success = c.login(username=farmer_username, password='pass123')
    if login_success:
        print("✅ Login Successful")
    else:
        print("❌ Login Failed")
        return

    # 3. Dashboard Access
    print("\n[STEP 3] Access Dashboard")
    resp = c.get('/dashboard/')
    if resp.status_code == 200:
        content = resp.content.decode()
        if "Dashboard Overview" in content:
            print("✅ Dashboard loaded successfully")
        else:
            print("❌ Dashboard content missing")
        
        # Check for new "Browse Marketplace" button
        if "Browse Marketplace" in content:
            print("✅ 'Browse Marketplace' button is VISIBLE")
        else:
            print("❌ 'Browse Marketplace' button is MISSING in Dashboard")
    else:
        print(f"❌ Dashboard failed to load (Status: {resp.status_code})")

    # 4. Create Listing
    print("\n[STEP 4] Create Listing")
    with open('verify_farmer_journey.py', 'rb') as fp: # Dummy file for image
        post_data = {
            'title': 'Preview Carrots',
            'description': 'Fresh carrots',
            'category': cat.id,
            'price': 50,
            'quantity': 100,
            'unit': 'KG',
            'expiry_date': '2025-12-31',
            # 'image': fp # Skip image for simplicity in manual script, form might allow empty or we rely on required=False if model allows, but form has it?
            # Model has image=models.ImageField(upload_to='listings/', blank=True, null=True) usually? Let's check model if it fails.
        }
        resp = c.post('/create_listing/', post_data, follow=True)
        if resp.status_code == 200:
            # Should redirect to home or dashboard? View redirects to 'home'
            # Let's check if listing exists
            if Listing.objects.filter(title='Preview Carrots').exists():
                 print("✅ Listing 'Preview Carrots' created successfully")
            else:
                 print("❌ Listing creation failed (Database)")
                 print("Response Status:", resp.status_code)
                 # print(resp.content.decode()) # Uncomment if needed
        else:
            print(f"❌ Create listing request failed (Status: {resp.status_code})")

    # 5. Order Management (Simulate an order)
    print("\n[STEP 5] Order Management")
    try:
        listing = Listing.objects.get(title='Preview Carrots')
        order = Order.objects.create(listing=listing, buyer=buyer_user, quantity=5, status='PENDING')
        
        # Reload dashboard to see order
        resp = c.get('/dashboard/')
        if str(order.id) in resp.content.decode():
            print("✅ Order #{} is visible in Dashboard".format(order.id))
        else:
            print("❌ Order #{} NOT visible in Dashboard".format(order.id))

        # Update Status
        resp = c.post(f'/update_order_status/{order.id}/', {'status': 'SHIPPED'}, follow=True)
        order.refresh_from_db()
        if order.status == 'SHIPPED':
            print("✅ Order status updated to SHIPPED")
        else:
            print(f"❌ Order status update failed. Current: {order.status}")
    except Listing.DoesNotExist:
        print("❌ Step 5 Skipped: Listing creation failed previously.")

    # 6. Analytics
    print("\n[STEP 6] Analytics")
    resp = c.get('/analytics/')
    if resp.status_code == 200:
        content = resp.content.decode()
        # Check for JSON data presence
        if 'daily_sales' in content and 'top_products' in content:
            print("✅ Analytics page loaded with data context")
        else:
            print("❌ Analytics page missing data context")
    else:
        print(f"❌ Analytics page failed to load (Status: {resp.status_code})")

    # 7. Marketplace Access
    print("\n[STEP 7] Marketplace Visibility")
    # Verify we can see it
    resp = c.get('/') # Home
    if resp.status_code == 200:
        content = resp.content.decode()
        if "Browse Marketplace" in content or "Fresh Farm Produce" in content: # Hero section text
             print("✅ Home/Marketplace page accessible")
             # Check if we see our own listing
             if "Preview Carrots" in content:
                 print("✅ Own listing visible in marketplace")
        else:
             print("❌ Home page content suspicious")
    else:
        print(f"❌ Home page failed (Status: {resp.status_code})")

    print("\n--- Verification Complete ---")

if __name__ == '__main__':
    verify_farmer_journey()
