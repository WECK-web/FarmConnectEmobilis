import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Category, Listing, Order

def test_complete_workflow():
    """
    Test the complete application workflow:
    1. Register a farmer
    2. Farmer creates a listing
    3. Register a consumer
    4. Consumer adds to cart and checks out
    5. Farmer views order
    """
    client = Client()
    print("\n=== TESTING COMPLETE WORKFLOW ===\n")
    
    # Cleanup
    try:
        User.objects.filter(username__in=['testfarmer_complete', 'testconsumer_complete']).delete()
        Category.objects.filter(name='TestCategory').delete()
    except:
        pass
    
    # 1. Register Farmer
    print("1. Registering Farmer...")
    farmer_data = {
        'username': 'testfarmer_complete',
        'email': 'farmer_complete@test.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!',
        'user_type': 'FARMER'
    }
    resp = client.post(reverse('register'), farmer_data, follow=True)
    farmer = User.objects.filter(username='testfarmer_complete').first()
    if not farmer:
        print(f"   [FAIL] Farmer registration failed")
        return
    print(f"   [SUCCESS] Farmer registered: {farmer.username} (Type: {farmer.profile.user_type})")
    
    # 2. Farmer Creates Listing
    print("\n2. Farmer creating listing...")
    client.login(username='testfarmer_complete', password='TestPass123!')
    
    # Create category first
    cat = Category.objects.create(name='TestCategory')
    
    listing_data = {
        'title': 'Fresh Tomatoes',
        'category': cat.id,
        'description': 'Organic homegrown tomatoes',
        'quantity': 50,
        'unit': 'KG',
        'price': 5.99,
        'expiry_date': '2025-12-31'
    }
    resp = client.post(reverse('create_listing'), listing_data, follow=True)
    listing = Listing.objects.get(title='Fresh Tomatoes')
    print(f"   [SUCCESS] Listing created: {listing.title} (${listing.price} per {listing.unit})")
    
    # 3. Register Consumer
    print("\n3. Registering Consumer...")
    client.logout()
    consumer_data = {
        'username': 'testconsumer_complete',
        'email': 'consumer_complete@test.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!',
        'user_type': 'CONSUMER'
    }
    resp = client.post(reverse('register'), consumer_data, follow=True)
    consumer = User.objects.filter(username='testconsumer_complete').first()
    if not consumer:
        print(f"   [FAIL] Consumer registration failed")
        return
    print(f"   [SUCCESS] Consumer registered: {consumer.username} (Type: {consumer.profile.user_type})")
    
    # 4. Consumer Adds to Cart
    print("\n4. Consumer adding to cart...")
    client.login(username='testconsumer_complete', password='TestPass123!')
    resp = client.post(reverse('cart_add', args=[listing.id]), follow=True)
    
    cart_session = client.session.get('cart', {})
    if str(listing.id) in cart_session:
        print(f"   [SUCCESS] Item added to cart: {listing.title}")
    else:
        print(f"   [FAIL] Failed to add to cart")
        return
    
    # 5. Consumer Checks Out
    print("\n5. Consumer checking out...")
    initial_qty = listing.quantity
    resp = client.post(reverse('checkout'), follow=True)
    
    # Verify order created
    order = Order.objects.filter(buyer=consumer, listing=listing).first()
    if order:
        print(f"   [SUCCESS] Order created: Order #{order.id}")
    else:
        print(f"   [FAIL] Order creation failed")
        return
    
    # Verify inventory decreased
    listing.refresh_from_db()
    if listing.quantity < initial_qty:
        print(f"   [SUCCESS] Inventory updated: {initial_qty} -> {listing.quantity} {listing.unit}")
    else:
        print(f"   [FAIL] Inventory not updated")
    
    # 6. Farmer Views Dashboard
    print("\n6. Farmer viewing dashboard...")
    client.logout()
    client.login(username='testfarmer_complete', password='TestPass123!')
    resp = client.get(reverse('farmer_dashboard'))
    
    if resp.status_code == 200 and 'orders' in resp.context:
        orders = resp.context['orders']
        if orders.filter(id=order.id).exists():
            print(f"   [SUCCESS] Order visible on farmer dashboard")
        else:
            print(f"   [FAIL] Order not visible on dashboard")
    else:
        print(f"   [FAIL] Dashboard error")
    
    # 7. Test Access Control
    print("\n7. Testing access control...")
    
    # Try farmer adding to cart (should fail)
    resp = client.post(reverse('cart_add', args=[listing.id]), follow=True)
    cart_after_farmer = client.session.get('cart', {})
    
    if str(listing.id) not in cart_after_farmer or len(cart_after_farmer) == 0:
        print(f"   [SUCCESS] Farmers correctly blocked from cart")
    else:
        print(f"   [FAIL] Farmers can add to cart (security issue!)")
    
    # Try consumer creating listing (should fail)
    client.logout()
    client.login(username='testconsumer_complete', password='TestPass123!')
    resp = client.get(reverse('create_listing'), follow=True)
    
    if resp.redirect_chain and 'home' in resp.redirect_chain[-1][0]:
        print(f"   [SUCCESS] Consumers correctly blocked from creating listings")
    else:
        print(f"   [FAIL] Consumers can access create listing page")
    
    print("\n=== WORKFLOW TEST COMPLETE ===\n")
    
    # Cleanup
    print("Cleaning up test data...")
    User.objects.filter(username__in=['testfarmer_complete', 'testconsumer_complete']).delete()
    Category.objects.filter(name='TestCategory').delete()
    print("[SUCCESS] Cleanup complete\n")

if __name__ == '__main__':
    test_complete_workflow()
