import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Category, Order

def print_result(name, success, msg=""):
    status = "SUCCESS" if success else "FAILURE"
    print(f"[{status}] {name}: {msg}")

def verify_health():
    print("\n--- Final System Health Check ---")
    client = Client()

    # 1. Test Home Page (Template Rendering)
    try:
        response = client.get(reverse('home'))
        if response.status_code == 200:
            print_result("Home Page Load", True, "Status 200 OK")
        else:
            print_result("Home Page Load", False, f"Status {response.status_code}")
    except Exception as e:
        print_result("Home Page Load", False, f"Exception: {str(e)}")

    # 2. Test Inventory Deduction
    try:
        # Setup
        seller = User.objects.create_user('health_seller', 'seller@test.com', 'pass')
        seller.profile.user_type = 'FARMER'
        seller.profile.save()
        
        buyer = User.objects.create_user('health_buyer', 'buyer@test.com', 'pass')
        buyer.profile.user_type = 'CONSUMER'
        buyer.profile.save()
        
        cat = Category.objects.create(name='Health Cat', image='test.jpg')
        listing = Listing.objects.create(
            seller=seller, title='Health Item', category=cat,
            description='Test', quantity=5, unit='kg', price=10.00, expiry_date='2025-01-01'
        )
        
        # Add to cart & checkout
        client.force_login(buyer)
        session = client.session
        session['cart'] = {str(listing.id): {'quantity': 2, 'price': 10.00}} 
        # Note: session update in test client needs save, but views.py reads direct from session or Cart class
        # Let's use the actual cart_add view ensuring SessionWorks
        client.post(reverse('cart_add', args=[listing.id])) # qty 1 default
        
        # Checkout
        client.post(reverse('checkout'))
        
        # Check inventory
        listing.refresh_from_db()
        if listing.quantity == 4: # Started 5, bought 1 (default add)
            print_result("Inventory Logic", True, f"Quantity dropped to {listing.quantity}")
        else:
            print_result("Inventory Logic", False, f"Quantity is {listing.quantity} (Expected 4)")
            
    except Exception as e:
        print_result("Inventory Logic", False, f"Exception: {str(e)}")
    
    # Cleanup
    try:
        seller.delete()
        buyer.delete()
        cat.delete()
    except:
        pass

if __name__ == '__main__':
    verify_health()
