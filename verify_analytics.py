
import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from core.models import Order
from core.views import farmer_analytics

try:
    # 1. Setup Data
    farmer = User.objects.get(username='farmer_test')
    
    # Ensure at least one COMPLETED order exists
    order = Order.objects.filter(listing__seller=farmer).first()
    if order:
        order.status = 'CANCELLED'
        order.save()
        print(f"Order {order.id} marked CANCELLED for testing.")
    else:
        print("No order found for farmer_test. Cannot verify analytics data.")
        
    # Ensure profile is complete (to pass @profile_required)
    profile = farmer.profile
    profile.phone = "0712345678"
    profile.location = "Nairobi, Kenya"
    profile.save()

    # 2. Simulate Request
    factory = RequestFactory()
    request = factory.get('/analytics/')
    request.user = farmer
    
    # Mock profile (since view uses @profile_required and user.profile access)
    # The middleware/decorators usually handle this, but factory doesn't running middleware.
    # However, user.profile access in view (line 1831) works if related object exists.
    
    # Mock middleware support
    from django.contrib.messages.storage.fallback import FallbackStorage
    request.session = {}
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # 3. Call View
    response = farmer_analytics(request)
    
    if response.status_code == 200:
        print("Analytics Page Load: SUCCESS (200 OK)")
        content = response.content.decode('utf-8')
        
        # 4. Check for JSON data presence
        if 'const categoryData = JSON.parse' in content:
             print("Category Data JavaScript found in template.")
        else:
             print("WARNING: Category Data JS not found in output (Template issue?)")

        # 5. Verify Context (By inspecting what was passed to render if possible, 
        # but with direct view call we get HttpResponse.)
        # faster way: check if the JSON string is present in the rendered HTML.
        # We know specific keys like 'Test Potatoes' should be there if data exists.
        
        if 'Test Potatoes' in content:
            print("Data Verification: Found 'Test Potatoes' in rendered analytics.")
        else:
             print("Data Verification: 'Test Potatoes' NOT found (Maybe not in top products?)")

    # 6. Verify CSV Download
    print("\nTesting CSV Download...")
    request_csv = factory.get('/analytics/download/')
    request_csv.user = farmer
    from core.views import download_sales_report
    response_csv = download_sales_report(request_csv)
    
    if response_csv.status_code == 200:
        print("CSV Download: SUCCESS (200 OK)")
        if response_csv['Content-Type'] == 'text/csv':
             print("CSV Content-Type: CORRECT")
        else:
             print(f"CSV Content-Type: WRONG ({response_csv['Content-Type']})")
    else:
        print(f"CSV Download: FAILED ({response_csv.status_code})")


        if response.status_code == 302:
            print(f"Redirect URL: {response.url}")

except Exception as e:
    print(f"Error: {e}")
