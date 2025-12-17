import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Order, Listing

print("FARMERS WITH REVENUE:")
print("=" * 50)

farmers = User.objects.filter(profile__user_type='FARMER')

for farmer in farmers:
    # Get their listings
    listings = Listing.objects.filter(seller=farmer)
    
    # Get orders for their products
    orders = Order.objects.filter(listing__seller=farmer).exclude(status='CANCELLED')
    
    if orders.exists():
        revenue = sum(o.quantity * o.listing.price for o in orders)
        print(f"\nUsername: {farmer.username}")
        print(f"  Listings: {listings.count()}")
        print(f"  Orders: {orders.count()}")
        print(f"  Revenue: KSh {revenue}")
        print(f"  Login to see this revenue!")
        
print("\n" + "=" * 50)
print("If no farmers listed above, you need to:")
print("  1. Create a buyer account")
print("  2. Browse listings")
print("  3. Add to cart and checkout")
