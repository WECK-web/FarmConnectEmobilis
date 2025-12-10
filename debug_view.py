import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import RequestFactory
from core.views import home
from core.models import Listing, Category, Profile
from django.contrib.auth.models import User
from decimal import Decimal

# Ensure data exists
if not User.objects.filter(username='farmer_debug').exists():
    u = User.objects.create_user('farmer_debug', 'password')
    Profile.objects.create(user=u, user_type='FARMER', location='Debug Land')
else:
    u = User.objects.get(username='farmer_debug')

if not Category.objects.filter(name='Debug Veg').exists():
    c = Category.objects.create(name='Debug Veg')
else:
    c = Category.objects.get(name='Debug Veg')

if not Listing.objects.filter(title='Fresh Carrots').exists():
    Listing.objects.create(
        seller=u, category=c, title='Fresh Carrots', 
        description='Debug carrots', quantity=10, unit='KG', 
        price=Decimal('5.00'), expiry_date='2025-12-31', is_available=True
    )
    print("Created 'Fresh Carrots' listing")
else:
    l = Listing.objects.get(title='Fresh Carrots')
    l.is_available = True
    l.save()
    print("Ensured 'Fresh Carrots' is available")

request = RequestFactory().get('/')
request.session = {}
try:
    response = home(request)
    print(f"Status Code: {response.status_code}")
    content = response.content.decode()
    if 'Fresh Carrots' in content:
        print("Found 'Fresh Carrots'")
    else:
        print("NOT Found 'Fresh Carrots'")
        print("Listings in DB:", Listing.objects.count())
        print("Available Listings:", Listing.objects.filter(is_available=True).count())
        # print(content) # Too long, maybe just a snippet if needed
except Exception as e:
    import traceback
    traceback.print_exc()
