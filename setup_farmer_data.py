
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Order, Profile, Category

try:
    farmer = User.objects.get(username='farmer_test')
    buyer = User.objects.get(username='admin_test') # Use admin as buyer
    
    # Create Category
    cat, _ = Category.objects.get_or_create(name="Test Category")

    # Create Listing
    listing, created = Listing.objects.get_or_create(
        seller=farmer,
        title="Test Potatoes",
        defaults={
            'description': "Fresh test potatoes",
            'price': 500,
            'quantity': 100,
            'unit': 'SACK',
            'category': cat,
            'expiry_date': timezone.now().date()
        }
    )
    
    # Create Order
    order = Order.objects.create(
        listing=listing,
        buyer=buyer,
        quantity=2,
        status='PENDING'
    )
    
    # Create OrderItem
    from core.models import OrderItem
    OrderItem.objects.create(
        order=order,
        listing=listing,
        price=500,
        quantity=2
    )

    print(f"Created Listing {listing.id} and Order {order.id} for {farmer.username}")

except Exception as e:
    print(f"Error: {e}")
