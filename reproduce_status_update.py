
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import Order, Listing, OrderStatusHistory
from core.views import update_order_status
from django.contrib.messages.storage.fallback import FallbackStorage

try:
    # 1. Setup Data
    farmer = User.objects.get(username='farmer_test')
    order = Order.objects.filter(listing__seller=farmer).first()
    
    if not order:
        print("No order found for farmer_test. Run setup_farmer_data.py first.")
        exit()

    print(f"Testing Update for Order {order.id} (Current Status: {order.status}) by Farmer {farmer.username}")

    # 2. Create Request
    factory = RequestFactory()
    url = f'/order/update/{order.id}/'
    data = {'status': 'CONFIRMED'} # Simulating the button click
    request = factory.post(url, data)
    request.user = farmer
    
    # Add message support (required by view)
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    # 3. Call View
    response = update_order_status(request, order.id)

    # 4. Check Result
    order.refresh_from_db()
    print(f"Response Status Code: {response.status_code}")
    print(f"New Order Status: {order.status}")
    
    if order.status == 'CONFIRMED':
        print("SUCCESS: Status updated.")
    else:
        print("FAILURE: Status did NOT update.")

except Exception as e:
    print(f"EXCEPTION: {e}")
