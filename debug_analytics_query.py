import os
import django
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncDate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.models import Order, Listing, User, Category

def debug_query():
    print("--- Debugging Query ---")
    u = User.objects.first()
    orders = Order.objects.filter(listing__seller=u)
    
    print("1. Testing Category Sales Query...")
    try:
        qs = orders.values('listing__category__name').annotate(total_revenue=Sum(F('quantity') * F('listing__price'))).order_by('-total_revenue')
        print(list(qs))
        print("✅ Category Sales Query OK")
    except Exception as e:
        print(f"❌ Category Sales Query Failed: {e}")

    print("2. Testing Daily Sales Query...")
    try:
        qs = orders.annotate(date=TruncDate('created_at')).values('date').annotate(total_sales=Sum(F('quantity') * F('listing__price'))).order_by('date')
        print(list(qs))
        print("✅ Daily Sales Query OK")
    except Exception as e:
        print(f"❌ Daily Sales Query Failed: {e}")

if __name__ == '__main__':
    debug_query()
