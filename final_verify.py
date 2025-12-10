import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Category, Profile

def test_all():
    print("\n=== COMPREHENSIVE SYSTEM VERIFICATION ===\n")
    client = Client()
    results = []
    
    # Test 1: Home Page
    try:
        resp = client.get('/')
        results.append(("Home Page Load", resp.status_code == 200, f"Status: {resp.status_code}"))
    except Exception as e:
        results.append(("Home Page Load", False, str(e)))
    
    # Test 2: Login Page
    try:
        resp = client.get('/login/')
        results.append(("Login Page", resp.status_code == 200, f"Status: {resp.status_code}"))
    except Exception as e:
        results.append(("Login Page", False, str(e)))
    
    # Test 3: Registration
    try:
        resp = client.post('/register/', {
            'username': 'testfarmer2',
            'email': 'farmer2@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'FARMER'
        })
        user_created = User.objects.filter(username='testfarmer2').exists()
        results.append(("User Registration", user_created, "Farmer created"))
    except Exception as e:
        results.append(("User Registration", False, str(e)))
    
    # Test 4: Profile Auto-Creation
    try:
        user = User.objects.get(username='testfarmer2')
        has_profile = hasattr(user, 'profile') and user.profile.user_type == 'FARMER'
        results.append(("Profile Auto-Creation", has_profile, "Profile exists with correct type"))
    except Exception as e:
        results.append(("Profile Auto-Creation", False, str(e)))
    
    # Test 5: Login Redirect (Farmer -> Dashboard)
    try:
        client.login(username='testfarmer2', password='TestPass123!')
        resp = client.post('/login/', {
            'username': 'testfarmer2',
            'password': 'TestPass123!'
        }, follow=True)
        redirected_to_dashboard = '/dashboard/' in resp.redirect_chain[0][0] if resp.redirect_chain else False
        results.append(("Farmer Login Redirect", redirected_to_dashboard, "Redirects to dashboard"))
    except Exception as e:
        results.append(("Farmer Login Redirect", False, str(e)))
    
    # Test 6: Cart Access (Farmers blocked)
    try:
        cat = Category.objects.first() or Category.objects.create(name='Test', image='test.jpg')
        listing = Listing.objects.create(
            seller=user, title='Test Item', category=cat,
            description='Test', quantity=10, unit='kg', price=5.00, expiry_date='2025-01-01'
        )
        resp = client.post(f'/cart/add/{listing.id}/')
        # Should redirect (not add to cart) because user is FARMER
        cart_empty = len(client.session.get('cart', {})) == 0
        results.append(("Farmer Cart Block", cart_empty, "Farmers cannot add to cart"))
    except Exception as e:
        results.append(("Farmer Cart Block", False, str(e)))
    
    # Test 7: Consumer Cart & Checkout
    try:
        consumer = User.objects.create_user('testconsumer2', 'consumer2@test.com', 'TestPass123!')
        consumer.profile.user_type = 'CONSUMER'
        consumer.profile.save()
        
        client.logout()
        client.login(username='testconsumer2', password='TestPass123!')
        
        resp = client.post(f'/cart/add/{listing.id}/')
        cart_has_item = str(listing.id) in client.session.get('cart', {})
        results.append(("Consumer Add to Cart", cart_has_item, "Item added successfully"))
        
        # Checkout
        initial_qty = listing.quantity
        resp = client.post('/checkout/')
        listing.refresh_from_db()
        inventory_reduced = listing.quantity < initial_qty
        results.append(("Inventory Deduction", inventory_reduced, f"Qty: {initial_qty} -> {listing.quantity}"))
        
    except Exception as e:
        results.append(("Consumer Checkout", False, str(e)))
    
    # Print Results
    print("\n--- TEST RESULTS ---")
    for name, passed, msg in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {name}: {msg}")
    
    # Cleanup
    try:
        User.objects.filter(username__startswith='test').delete()
        Category.objects.filter(name='Test').delete()
    except:
        pass

if __name__ == '__main__':
    test_all()
