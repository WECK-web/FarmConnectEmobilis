import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Category, Listing, Order
from decimal import Decimal
from datetime import datetime, timedelta

print("Creating Test Data for Revenue Analytics...")
print("=" * 60)

# 1. Create/Get Test Farmer
farmer_username = "revenue_farmer"
farmer, created = User.objects.get_or_create(
    username=farmer_username,
    defaults={
        'email': 'revenue_farmer@test.com',
        'first_name': 'John',
        'last_name': 'Farmer'
    }
)
if created:
    farmer.set_password('testpass123')
    farmer.save()
    print(f"✓ Created farmer: {farmer_username}")
else:
    print(f"✓ Using existing farmer: {farmer_username}")

# Ensure profile
profile, created = Profile.objects.get_or_create(
    user=farmer,
    defaults={
        'user_type': 'FARMER',
        'phone': '0712345678',
        'location': 'Nairobi, Kenya',
        'latitude': -1.286389,
        'longitude': 36.817223
    }
)
if created:
    print(f"✓ Created profile for farmer")
elif profile.user_type != 'FARMER':
    profile.user_type = 'FARMER'
    profile.phone = '0712345678'
    profile.location = 'Nairobi, Kenya'
    profile.save()
    print(f"✓ Updated profile to FARMER")

# 2. Create/Get Categories
veggies, _ = Category.objects.get_or_create(name='Vegetables')
fruits, _ = Category.objects.get_or_create(name='Fruits')
grains, _ = Category.objects.get_or_create(name='Grains')
print(f"✓ Categories ready")

# 3. Create Listings
listings_data = [
    {'title': 'Fresh Tomatoes', 'category': veggies, 'price': 200, 'quantity': 100},
    {'title': 'Organic Potatoes', 'category': veggies, 'price': 150, 'quantity': 200},
    {'title': 'Sweet Mangoes', 'category': fruits, 'price': 300, 'quantity': 50},
    {'title': 'White Maize', 'category': grains, 'price': 500, 'quantity': 150},
]

created_listings = []
for data in listings_data:
    listing, created = Listing.objects.get_or_create(
        seller=farmer,
        title=data['title'],
        defaults={
            'category': data['category'],
            'price': Decimal(data['price']),
            'quantity': data['quantity'],
            'description': f"High quality {data['title'].lower()}",
            'expiry_date': (datetime.now() + timedelta(days=30)).date()
        }
    )
    created_listings.append(listing)
    if created:
        print(f"✓ Created listing: {data['title']} - KSh {data['price']}")
    else:
        print(f"✓ Using existing listing: {data['title']}")

# 4. Create/Get Test Buyer
buyer_username = "revenue_buyer"
buyer, created = User.objects.get_or_create(
    username=buyer_username,
    defaults={
        'email': 'buyer@test.com',
        'first_name': 'Jane',
        'last_name': 'Consumer'
    }
)
if created:
    buyer.set_password('testpass123')
    buyer.save()
    print(f"✓ Created buyer: {buyer_username}")
else:
    print(f"✓ Using existing buyer: {buyer_username}")

# Ensure buyer profile
buyer_profile, created = Profile.objects.get_or_create(
    user=buyer,
    defaults={
        'user_type': 'CONSUMER',
        'phone': '0723456789',
        'location': 'Nairobi, Kenya'
    }
)

# 5. Create Orders
orders_to_create = [
    {'listing': created_listings[0], 'quantity': 10, 'status': 'PENDING'},      # 10 x 200 = 2000
    {'listing': created_listings[1], 'quantity': 20, 'status': 'CONFIRMED'},    # 20 x 150 = 3000
    {'listing': created_listings[2], 'quantity': 5, 'status': 'SHIPPED'},       # 5 x 300 = 1500
    {'listing': created_listings[3], 'quantity': 4, 'status': 'DELIVERED'},     # 4 x 500 = 2000
]

total_revenue = 0
for order_data in orders_to_create:
    # Check if similar order exists
    existing = Order.objects.filter(
        listing=order_data['listing'],
        buyer=buyer,
        quantity=order_data['quantity']
    ).first()
    
    if not existing:
        order = Order.objects.create(
            listing=order_data['listing'],
            buyer=buyer,
            quantity=order_data['quantity'],
            status=order_data['status']
        )
        order_total = order.quantity * order.listing.price
        total_revenue += order_total
        print(f"✓ Created order: {order.listing.title} x{order.quantity} = KSh {order_total} ({order.status})")
    else:
        order_total = existing.quantity * existing.listing.price
        total_revenue += order_total
        print(f"✓ Using existing order: {existing.listing.title} x{existing.quantity} = KSh {order_total}")

print("=" * 60)
print(f"TOTAL EXPECTED REVENUE: KSh {total_revenue}")
print("=" * 60)
print(f"\nTo see the revenue:")
print(f"  1. Go to: http://127.0.0.1:8000/accounts/login/")
print(f"  2. Username: {farmer_username}")
print(f"  3. Password: testpass123")
print(f"  4. Visit: http://127.0.0.1:8000/analytics/")
print(f"\nYou should see revenue charts with KSh {total_revenue}!")
