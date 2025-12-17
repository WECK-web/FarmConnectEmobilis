import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Order

# Check ALL farmers with orders
farmers_with_orders = User.objects.filter(
    profile__user_type='FARMER',
    seller_listings__order__isnull=False
).distinct()

print(f"Farmers with orders: {farmers_with_orders.count()}\n")

for farmer in farmers_with_orders:
    orders = Order.objects.filter(listing__seller=farmer)
    print(f"{farmer.username}:")
    print(f"  Total orders: {orders.count()}")
    
    # Status breakdown
    pending = orders.filter(status='PENDING').count()
    confirmed = orders.filter(status='CONFIRMED').count()
    processing = orders.filter(status='PROCESSING').count()
    shipped = orders.filter(status='SHIPPED').count()
    delivered = orders.filter(status='DELIVERED').count()
    cancelled = orders.filter(status='CANCELLED').count()
    
    print(f"  PENDING: {pending}, CONFIRMED: {confirmed}, PROCESSING: {processing}")
    print(f"  SHIPPED: {shipped}, DELIVERED: {delivered}, CANCELLED: {cancelled}")
    
    # Calculate revenue
    active_orders = orders.exclude(status='CANCELLED')
    if active_orders.exists():
        total = sum(o.quantity * o.listing.price for o in active_orders)
        print(f"  Expected Revenue: KSh {total}")
    else:
        print(f"  Expected Revenue: KSh 0 (all cancelled)")
    print()
