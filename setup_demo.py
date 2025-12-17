import os
import django
import sys
# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farm_connect.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Listing, Category, Order
from django.utils import timezone
from datetime import timedelta
import random

def setup_demo():
    print("Setting up Demo Farmer Account...")
    username = "demo_farmer"
    password = "password123"
    
    # 1. Create/Get User
    try:
        user = User.objects.get(username=username)
        print(f"User {username} already exists. Resetting data...")
        Listing.objects.filter(seller=user).delete() # Cascade deletes orders
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password)
        print(f"Created user: {username}")
        
    # 2. Setup Profile
    p, _ = Profile.objects.get_or_create(user=user)
    p.user_type = 'FARMER'
    p.phone = '555-0199'
    p.location = 'Green Valley, CA'
    p.save()
    
    # 3. Create Categories & Products
    vege_cat, _ = Category.objects.get_or_create(name="Vegetables")
    fruit_cat, _ = Category.objects.get_or_create(name="Fruits")
    
    products = [
        {"title": "Organic Carrots", "price": 12, "cat": vege_cat},
        {"title": "Fresh Tomatoes", "price": 15, "cat": vege_cat},
        {"title": "Sweet Strawberries", "price": 25, "cat": fruit_cat},
        {"title": "Potatoes", "price": 8, "cat": vege_cat},
        {"title": "Honeycrisp Apples", "price": 20, "cat": fruit_cat},
    ]
    
    listings = []
    for prod in products:
        l = Listing.objects.create(
            seller=user,
            title=prod["title"],
            price=prod["price"],
            category=prod["cat"],
            quantity=100,
            unit="kg"
        )
        listings.append(l)
        
    # 4. Create Sales History (Past 7 days)
    print("Generating sales history...")
    for i in range(7):
        day = timezone.now() - timedelta(days=i)
        # Random daily sales
        daily_orders = random.randint(3, 8)
        
        for _ in range(daily_orders):
            prod = random.choice(listings)
            Order.objects.create(
                listing=prod,
                buyer=user, # Buying own stuff for demo simplicity (or create dummy buyer)
                status='COMPLETED',
                quantity=random.randint(1, 5),
                date_ordered=day
            )
            
    # Add some pending orders
    Order.objects.create(listing=listings[0], buyer=user, status='PENDING', date_ordered=timezone.now())
    Order.objects.create(listing=listings[2], buyer=user, status='PENDING', date_ordered=timezone.now())

    print("\nSUCCESS! Demo Account Ready.")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("Login and visit 'Analytics' to see the charts.")

if __name__ == "__main__":
    setup_demo()
