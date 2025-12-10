import os
import django
from django.test import Client
from django.urls import reverse
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Listing, Order

def print_result(test_name, success, message=""):
    status = "SUCCESS" if success else "FAILURE"
    print(f"[{status}] {test_name}: {message}")

def verify_features():
    client = Client()
    
    # 1. Registration & Profile Creation
    print("\n--- Testing Registration ---")
    
    # Register Farmer
    farmer_data = {
        'username': 'verif_farmer',
        'email': 'farmer@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'FARMER'
    }
    response = client.post(reverse('register'), farmer_data)
    farmer = User.objects.filter(username='verif_farmer').first()
    
    if farmer and hasattr(farmer, 'profile') and farmer.profile.user_type == 'FARMER':
        print_result("Farmer Registration", True, "Profile created with correct role.")
    else:
        if 'form' in response.context:
            print(f"DEBUG: Form Errors: {response.context['form'].errors}")
        print_result("Farmer Registration", False, "Failed to create farmer profile.")
        return # Stop if basic auth fails

    # Register Consumer
    consumer_data = {
        'username': 'verif_consumer',
        'email': 'consumer@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'CONSUMER'
    }
    client.post(reverse('register'), consumer_data)
    consumer = User.objects.filter(username='verif_consumer').first()
    
    if consumer and hasattr(consumer, 'profile') and consumer.profile.user_type == 'CONSUMER':
        print_result("Consumer Registration", True, "Profile created with correct role.")
    else:
        print_result("Consumer Registration", False)

    # 2. Listing Management (Farmer)
    print("\n--- Testing Listing Management ---")
    client.force_login(farmer)
    
    # Create Listing
    listing_data = {
        'title': 'Test Tomato',
        'category': '', # Assuming nullable or handled
        'description': 'Delicious red tomatoes',
        'quantity': 100,
        'unit': 'KG',
        'price': 5.50,
        'expiry_date': '2025-12-31',
        # Image is tricky in tests, skipping file upload verification to keep simple
    }
    response = client.post(reverse('create_listing'), listing_data)
    listing = Listing.objects.filter(title='Test Tomato').first()
    
    if listing and listing.seller == farmer:
        print_result("Create Listing", True, "Listing created by farmer.")
    else:
        print_result("Create Listing", False, "Listing creation failed.")

    # Edit Listing
    if listing:
        edit_data = listing_data.copy()
        edit_data['price'] = 6.00
        response = client.post(reverse('edit_listing', args=[listing.id]), edit_data)
        listing.refresh_from_db()
        
        if listing.price == 6.00:
            print_result("Edit Listing", True, "Price updated successfully.")
        else:
            print_result("Edit Listing", False, "Price update failed.")
            
    # 3. Access Control (Consumer)
    print("\n--- Testing Access Control ---")
    client.force_login(consumer)
    response = client.get(reverse('create_listing'))
    
    if response.status_code == 302 and response.url == reverse('home'): # Expect redirect to home
         print_result("Restrict Create Listing", True, "Consumer redirected from create page.")
    else:
         print_result("Restrict Create Listing", False, f"Consumer accessed page (Status: {response.status_code})")

    # 4. Consumer Orders
    print("\n--- Testing Orders ---")
    # Manually create order (skipping cart flow complexity for unit test speed)
    if listing:
        order = Order.objects.create(listing=listing, buyer=consumer, status='PENDING')
        
        response = client.get(reverse('consumer_orders'))
        if 'Test Tomato' in str(response.content):
             print_result("View My Orders", True, "Order visible in consumer dashboard.")
        else:
             print_result("View My Orders", False, "Order not found in dashboard.")

    # 5. Profile Update
    print("\n--- Testing Profile Update ---")
    client.force_login(consumer)
    update_data = {
        'username': 'verif_consumer',
        'email': 'newemail@test.com',
        'first_name': 'Testy',
        'last_name': 'McTest',
        'phone': '1234567890',
        'location': 'Farmville'
    }
    response = client.post(reverse('profile'), update_data)
    consumer.refresh_from_db()
    consumer.profile.refresh_from_db()
    
    if consumer.email == 'newemail@test.com' and consumer.profile.location == 'Farmville':
        print_result("Update Profile", True, "Email and Location updated.")
    else:
        print_result("Update Profile", False, "Profile update failed.")

    # 6. Check Cart/Checkout Restriction (Farmer/Admin)
    print("\n--- Testing Checkout Restrictions ---")
    try:
        # Use existing farmer from setup
        client.force_login(farmer)
        
        # Try to add to cart
        # (Need a valid listing ID, so create one if needed or use existing)
        if listing:
            # Depending on implementation, add to cart is POST
            resp = client.post(reverse('cart_add', args=[listing.id]), follow=True)
            # Check if redirected to home (landing page)
            if resp.redirect_chain and resp.redirect_chain[-1][0] == '/':
                print_result("Restriction: Cart Add", True, "Farmer blocked and diverted to Home.")
            else:
                 print_result("Restriction: Cart Add", False, f"Farmer NOT blocked. URL: {resp.request['PATH_INFO']}")
        
        # Try to access checkout
        resp = client.get(reverse('checkout'), follow=True)
        if resp.redirect_chain and resp.redirect_chain[-1][0] == '/': 
             print_result("Restriction: Checkout", True, "Farmer blocked from checkout page.")
        else:
             print_result("Restriction: Checkout", False, f"Farmer NOT blocked. URL: {resp.request['PATH_INFO']}")

    except Exception as e:
         print_result("Restriction Test", False, f"Exception: {e}")

    # Cleanup
    if farmer: farmer.delete()
    if consumer: consumer.delete()

if __name__ == '__main__':
    verify_features()
