import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.models import Order

# Quick check
farmer_orders = Order.objects.filter(listing__seller__username='revenue_farmer')
print(f"Orders for revenue_farmer: {farmer_orders.count()}")

if farmer_orders.exists():
    active = farmer_orders.exclude(status='CANCELLED')
    revenue = sum(o.quantity * o.listing.price for o in active)
    print(f"Active orders: {active.count()}")
    print(f"Total Revenue: KSh {revenue}")
    
    for order in active:
        print(f"  - {order.listing.title} x{order.quantity} = KSh {order.total_price} [{order.status}]")
