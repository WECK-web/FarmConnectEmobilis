import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.models import Order

# Check ALL orders
total_orders = Order.objects.all()
print(f"Total orders in database: {total_orders.count()}\n")

if total_orders.count() == 0:
    print("NO ORDERS FOUND - This is why revenue is 0!")
    print("You need to:")
    print("  1. Log in as a buyer")
    print("  2. Add items to cart")
    print("  3. Complete checkout")
else:
    # Status breakdown
    print("Order Status Breakdown:")
    for status_code, status_label in Order.STATUS_CHOICES:
        count = total_orders.filter(status=status_code).count()
        if count > 0:
            orders_this_status = total_orders.filter(status=status_code)
            revenue = sum(o.quantity * o.listing.price for o in orders_this_status)
            print(f"  {status_label} ({status_code}): {count} orders, KSh {revenue}")
    
    # Check cancelled vs active
    cancelled = total_orders.filter(status='CANCELLED').count()
    active = total_orders.exclude(status='CANCELLED').count()
    
    print(f"\nActive orders (non-cancelled): {active}")
    print(f"Cancelled orders: {cancelled}")
    
    if active == 0:
        print("\nALL ORDERS ARE CANCELLED - This is why revenue is 0!")
    else:
        active_revenue = sum(o.quantity * o.listing.price for o in total_orders.exclude(status='CANCELLED'))
        print(f"\nExpected Revenue (active orders): KSh {active_revenue}")
