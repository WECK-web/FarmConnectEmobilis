import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Order, Listing

print("=" * 60)
print("REVENUE DEBUG REPORT")
print("=" * 60)

# Check all farmers
farmers = User.objects.filter(profile__user_type='FARMER')
print(f"\nFound {farmers.count()} farmer(s)")

for farmer in farmers:
    print(f"\n{'='*60}")
    print(f"Farmer: {farmer.username}")
    print(f"{'='*60}")
    
    # Check their listings
    listings = Listing.objects.filter(seller=farmer)
    print(f"  Listings: {listings.count()}")
    for listing in listings:
        print(f"    - {listing.title}: KSh {listing.price}")
    
    # Check orders for their products
    orders = Order.objects.filter(listing__seller=farmer)
    print(f"\n  Total Orders: {orders.count()}")
    
    if orders.count() == 0:
        print("  ❌ NO ORDERS FOUND - This is why revenue is 0!")
        continue
    
    # Break down by status
    for status_code, status_label in Order.STATUS_CHOICES:
        status_orders = orders.filter(status=status_code)
        count = status_orders.count()
        if count > 0:
            total_revenue = sum(o.total_price for o in status_orders)
            print(f"    {status_label}: {count} orders, KSh {total_revenue}")
    
    # Check what SHOULD be counted (non-cancelled)
    active_orders = orders.exclude(status='CANCELLED')
    print(f"\n  Active Orders (non-cancelled): {active_orders.count()}")
    
    if active_orders.count() == 0:
        print("  ❌ ALL ORDERS ARE CANCELLED - This is why revenue is 0!")
    else:
        total_active_revenue = sum(o.total_price for o in active_orders)
        print(f"  Expected Revenue: KSh {total_active_revenue}")
        
        # Show details of each active order
        print(f"\n  Active Order Details:")
        for order in active_orders:
            print(f"    Order #{order.id}:")
            print(f"      Listing: {order.listing.title}")
            print(f"      Price: KSh {order.listing.price}")
            print(f"      Quantity: {order.quantity}")
            print(f"      Total: KSh {order.total_price}")
            print(f"      Status: {order.status}")
            print(f"      Date: {order.date_ordered}")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
