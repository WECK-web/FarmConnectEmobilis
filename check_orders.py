import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Order

# Simple check
farmers = User.objects.filter(profile__user_type='FARMER')
print(f"Farmers: {farmers.count()}")

for farmer in farmers:
    print(f"\nFarmer: {farmer.username}")
    orders = Order.objects.filter(listing__seller=farmer)
    print(f"  Total orders: {orders.count()}")
    
    for status_code, status_label in Order.STATUS_CHOICES:
        count = orders.filter(status=status_code).count()
        if count > 0:
            print(f"    {status_code}: {count}")
    
    active = orders.exclude(status='CANCELLED').count()
    print(f"  Active (non-cancelled): {active}")
