
import os
import django
import sys
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Profile, Category, Listing, Order

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {msg}{colors['RESET']}")

def audit_farmer_flow():
    log("--- STARTING FARMER FLOW AUDIT ---")
    client = Client()
    
    # 1. Setup Data
    username = "audit_farmer"
    password = "password123"
    email = "farmer@audit.com"
    
    # Clean previous run
    if User.objects.filter(username=username).exists():
        User.objects.get(username=username).delete()
        
    # Create User
    user = User.objects.create_user(username=username, email=email, password=password)
    # Profile likely auto-created by signal
    if hasattr(user, 'profile'):
        user.profile.user_type = 'FARMER'
        user.profile.location = "Audit Farm"
        user.profile.save()
    else:
        Profile.objects.create(user=user, user_type='FARMER', location="Audit Farm")
    log(f"Created Farmer User: {username}", "SUCCESS")
    
    # Login
    login_success = client.login(username=username, password=password)
    if not login_success:
        log("Login Failed!", "ERROR")
        return
    log("Login Successful", "SUCCESS")
    
    # 2. Check Dashboard
    try:
        url = reverse('farmer_dashboard')
        resp = client.get(url)
        if resp.status_code == 200:
            log("Dashboard Loaded (200 OK)", "SUCCESS")
        else:
            log(f"Dashboard Failed: {resp.status_code}", "ERROR")
    except Exception as e:
        log(f"Dashboard Exception: {e}", "ERROR")

    # 3. Create Listing
    listing_id = None
    try:
        cat, _ = Category.objects.get_or_create(name="AuditVeg")
        url = reverse('create_listing')
        
        # Test GET first (Form rendering)
        resp_get = client.get(url)
        if resp_get.status_code == 200:
            log("Create Listing Page Loaded", "SUCCESS")
        else:
            log(f"Create Listing Page Failed: {resp_get.status_code}", "ERROR")

        # Test POST
        with open('c:/Users/HP/farm_project/static/img/hero_bg.jpg', 'rb') as fp: # Dummy image
             # We might not have this file, let's skip image or use SimpleUploadedFile if needed, 
             # but standard post without image might fail if required. 
             # ListingForm image is fields=['image'], model has blank=True? 
             # Listing model: image = models.ImageField(upload_to='listings/', blank=True, null=True)
             # Wait, form definition: image = forms.ClearableFileInput... 
             # Let's try without image first for simplicity
             data = {
                 'title': 'Audit Carrot',
                 'description': 'Fresh audit carrots',
                 'category': cat.id,
                 'price': 100,
                 'quantity': 50,
                 'unit': 'kg',
                 'expiry_date': '2025-12-31'
             }
             resp_post = client.post(url, data)
             if resp_post.status_code == 302:
                 log("Create Listing Redirected (Success)", "SUCCESS")
                 # Verify DB
                 listing = Listing.objects.get(title='Audit Carrot')
                 listing_id = listing.id
                 log(f"Listing Created ID: {listing.id}", "SUCCESS")
             else:
                 log(f"Create Listing Failed: {resp_post.status_code}", "ERROR")
                 if 'form' in resp_post.context:
                     log(f"Form Errors: {resp_post.context['form'].errors}", "ERROR")
    except Exception as e:
        log(f"Create Listing Exception: {e}", "ERROR")

    # 4. Edit Listing
    if listing_id:
        try:
            url = reverse('edit_listing', args=[listing_id])
            data = {
                 'title': 'Audit Carrot Edited',
                 'description': 'Fresh audit carrots',
                 'category': cat.id,
                 'price': 150, # Price change
                 'quantity': 50,
                 'unit': 'kg',
                 'expiry_date': '2025-12-31'
            }
            resp = client.post(url, data)
            if resp.status_code == 302:
                 log("Edit Listing Redirected (Success)", "SUCCESS")
                 updated = Listing.objects.get(id=listing_id)
                 if updated.price == 150:
                     log("Listing Price Updated to 150", "SUCCESS")
                 else:
                     log(f"Listing Price NOT Updated: {updated.price}", "ERROR")
            else:
                 log(f"Edit Listing Failed: {resp.status_code}", "ERROR")
        except Exception as e:
             log(f"Edit Listing Exception: {e}", "ERROR")
             
    # 5. Check Farmer Orders View (Empty)
    try:
        url = reverse('farmer_orders')
        resp = client.get(url)
        if resp.status_code == 200:
            log("Farmer Orders View Loaded (200 OK)", "SUCCESS")
        else:
            log(f"Farmer Orders View Failed: {resp.status_code}", "ERROR")
    except Exception as e:
        log(f"Farmer Orders Exception: {e}", "ERROR")

    # 6. Simulate Order & Status Update
    order_id = None
    if listing_id:
        try:
            # Create a consumer and order
            consumer = User.objects.create_user(username='audit_consumer', password='password123')
            order = Order.objects.create(
                buyer=consumer,
                listing_id=listing_id,
                quantity=5,
                total_price=750,
                status='PENDING'
            )
            order_id = order.id
            log(f"Created Test Order ID: {order_id}", "SUCCESS")
            
            # Try to update status
            url = reverse('update_order_status', args=[order_id])
            resp = client.post(url, {'status': 'COMPLETED'})
            if resp.status_code == 302:
                 log("Update Order Status Redirected (Success)", "SUCCESS")
                 order.refresh_from_db()
                 if order.status == 'COMPLETED':
                     log("Order Status Changed to COMPLETED", "SUCCESS")
                 else:
                     log(f"Order Status NOT Changed: {order.status}", "ERROR")
            else:
                 log(f"Update Order Status Failed: {resp.status_code}", "ERROR")
        except Exception as e:
             log(f"Order Simulation Exception: {e}", "ERROR")

    # 7. Check Analytics
    try:
        url = reverse('farmer_analytics')
        resp = client.get(url)
        if resp.status_code == 200:
            log("Analytics View Loaded (200 OK)", "SUCCESS")
        else:
            log(f"Analytics View Failed: {resp.status_code}", "ERROR")
    except Exception as e:
        log(f"Analytics Exception: {e}", "ERROR")

    log("--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    audit_farmer_flow()
