import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Order, Category

def verify_checkout():
    print("\n--- Verifying Checkout Flow ---")
    client = Client()

    # Setup Data
    farmer = User.objects.create_user(username='check_farmer', password='password123')
    farmer.profile.user_type = 'FARMER'
    farmer.profile.save()

    consumer = User.objects.create_user(username='check_consumer', password='password123')
    consumer.profile.user_type = 'CONSUMER'
    consumer.profile.save()

    # Create dummy listing
    list_item = Listing.objects.create(
        seller=farmer, title='Checkout Corn', description='Sweet corn',
        quantity=10, unit='KG', price=3.00, expiry_date='2025-12-31'
    )
    
    print("1. Adding item to cart...")
    client.force_login(consumer)
    
    # Simulate adding to cart via session (since cart_add logic is simple)
    # Note: complex usage of Cart class might need actual POST to cart_add
    # Let's do it via view to be safe
    client.post(reverse('cart_add', args=[list_item.id]))
    
    session = client.session
    if str(list_item.id) in session.get('cart', {}):
        print("   [SUCCESS] Item added to cart.")
    else:
        print(f"   [FAILURE] Cart empty. Session: {session.get('cart')}")
        return

    print("2. Proceeding to Checkout...")
    # POST to checkout view
    response = client.post(reverse('checkout'))

    # Verify Order Creation
    order = Order.objects.filter(buyer=consumer, listing=list_item).first()
    if order:
        print(f"   [SUCCESS] Order created! ID: {order.id}, Status: {order.status}")
    else:
        print("   [FAILURE] Order object was NOT created.")

    # Verify Cart Cleared
    session = client.session
    if not session.get('cart'):
        print("   [SUCCESS] Cart cleared after checkout.")
    else:
        print(f"   [FAILURE] Cart NOT cleared. Content: {session.get('cart')}")

    # Verify Success Page
    if response.status_code == 200 and 'order_success.html' in [t.name for t in response.templates]:
         print("   [SUCCESS] Redirected to success page.")
    else:
         print(f"   [WARNING] Response verify: Status {response.status_code}")

    # Cleanup
    farmer.delete()
    consumer.delete()

if __name__ == '__main__':
    verify_checkout()
