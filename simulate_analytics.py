import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Listing, Order, Category, Profile
from django.test import Client, RequestFactory
from core.views import farmer_analytics, download_sales_report

def simulate_analytics():
    print("--- Simulating Analytics ---")
    
    # 1. Setup Farmer and Data
    f, _ = User.objects.get_or_create(username='analytics_farmer')
    Profile.objects.update_or_create(user=f, defaults={'user_type': 'FARMER'})
    
    c1, _ = Category.objects.get_or_create(name='Fruits')
    c2, _ = Category.objects.get_or_create(name='Vegetables')
    
    l1, _ = Listing.objects.get_or_create(seller=f, title='Apple', defaults={'price': 10, 'quantity': 100, 'category': c1, 'expiry_date': '2025-12-31'})
    l2, _ = Listing.objects.get_or_create(seller=f, title='Carrot', defaults={'price': 5, 'quantity': 100, 'category': c2, 'expiry_date': '2025-12-31'})
    
    b, _ = User.objects.get_or_create(username='analytics_buyer')
    Order.objects.create(listing=l1, buyer=b, quantity=5, status='COMPLETED') # 50 revenue
    Order.objects.create(listing=l2, buyer=b, quantity=10, status='PENDING')   # 50 revenue
    
    factory = RequestFactory()
    req = factory.get('/analytics/')
    req.user = f
    
    # 2. Test View Logic
    print("\n[TEST 1] Farmer Analytics View")
    try:
        resp = farmer_analytics(req)
        content = resp.content.decode()
        
        # Check if context data is present in the rendered HTML (JSON stringify)
        # Search for "Fruits" or "Vegetables" to confirm category data
        if 'Fruits' in content and 'Vegetables' in content: 
            print("✅ Analytics data rendered correctly (Categories found)")
        else:
            print("❌ Analytics data missing or incorrect")
            print(f"Snippet: {content[:1000]}...") # Print first 1000 chars to debug
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ View raised exception: {e}")
        
    # 3. Test CSV Download
    print("\n[TEST 2] CSV Export")
    req = factory.get('/analytics/download/')
    req.user = f
    resp = download_sales_report(req)
    
    if resp['Content-Type'] == 'text/csv':
        content = resp.content.decode()
        lines = content.strip().split('\n')
        print(f"✅ CSV Header: {lines[0]}")
        
        if len(lines) >= 3: # Header + 2 rows
            print("✅ CSV contains data rows")
        else:
            print(f"❌ CSV missing rows (Rows: {len(lines)})")
            
    else:
        print("❌ Invalid Content-Type for CSV")

    print("\n--- Analytics Simulation Complete ---")

if __name__ == '__main__':
    simulate_analytics()
