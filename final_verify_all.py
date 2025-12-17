import os
import django
from django.test import Client, RequestFactory
from django.urls import reverse
from django.db.models import Avg

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Listing, Order, Review, Message
from core.views import custom_404, custom_500
from django.contrib.auth.models import AnonymousUser

def print_params(name, result, msg=""):
    symbol = "[PASS]" if result else "[FAIL]"
    output = f"{symbol} [{name}] {msg}\n"
    print(output.strip())
    with open("final_verify.log", "a") as f:
        f.write(output)

def verify_auth_and_profiles():
    print("\n--- 1. Authentication & Profiles ---")
    client = Client()
    
    # Cleanup
    User.objects.filter(username__in=['v_farmer', 'v_consumer']).delete()
    
    # Register Farmer
    f_data = {'username': 'v_farmer', 'email': 'f@t.com', 'password': 'pass', 'confirm_password': 'pass', 'user_type': 'FARMER'}
    client.post(reverse('register'), f_data)
    farmer = User.objects.filter(username='v_farmer').first()
    
    if farmer and farmer.profile.user_type == 'FARMER':
        print_params("Farmer Registration", True)
    else:
        print_params("Farmer Registration", False, "Failed")
        return None, None

    # Register Consumer
    c_data = {'username': 'v_consumer', 'email': 'c@t.com', 'password': 'pass', 'confirm_password': 'pass', 'user_type': 'CONSUMER'}
    client.post(reverse('register'), c_data)
    consumer = User.objects.filter(username='v_consumer').first()
    
    if consumer and consumer.profile.user_type == 'CONSUMER':
        print_params("Consumer Registration", True)
    else:
        print_params("Consumer Registration", False, "Failed")
    
    return farmer, consumer

def verify_profile_enforcement(farmer, consumer):
    print("\n--- 2. Profile Enforcement ---")
    client = Client()
    
    # Ensure incomplete profiles
    farmer.profile.phone = ''
    farmer.profile.location = ''
    farmer.profile.save()
    
    consumer.profile.phone = ''
    consumer.profile.location = ''
    consumer.profile.save()
    
    # Test Farmer Creating Listing
    client.force_login(farmer)
    resp = client.get(reverse('create_listing'), follow=True)
    if 'profile' in resp.request['PATH_INFO']:
        print_params("Enforce Farmer Profile", True, "Redirected to profile when creating listing")
    else:
        print_params("Enforce Farmer Profile", False, "Not redirected")

    # Test Consumer Adding to Cart
    # Need a listing
    dummy_seller = User.objects.create_user(username='d_seller', password='d')
    listing = Listing.objects.create(seller=dummy_seller, title='DItem', price=10, quantity=10, expiry_date='2025-12-31')
    
    client.force_login(consumer)
    resp = client.post(reverse('cart_add', args=[listing.id]), {'quantity': 1}, follow=True)
    
    if 'profile' in resp.request['PATH_INFO']:
        print_params("Enforce Consumer Profile", True, "Redirected to profile when adding to cart")
    else:
        print_params("Enforce Consumer Profile", False, "Not redirected")
    
    # Cleanup dummy
    dummy_seller.delete()

    # Fix profiles for next steps
    farmer.profile.phone = '123'
    farmer.profile.location = 'Barn'
    farmer.profile.save()
    
    consumer.profile.phone = '456'
    consumer.profile.location = 'City'
    consumer.profile.save()

def verify_core_features(farmer, consumer):
    print("\n--- 3. Core Features ---")
    client = Client()
    client.force_login(farmer)
    
    # Create Listing
    l_data = {
        'title': 'Real Tomato', 'category': '', 'description': 'desc',
        'quantity': 50, 'unit': 'KG', 'price': 5.00, 'expiry_date': '2025-12-31'
    }
    client.post(reverse('create_listing'), l_data)
    listing = Listing.objects.filter(title='Real Tomato', seller=farmer).first()
    
    if listing:
        print_params("Create Listing", True)
    else:
        print_params("Create Listing", False)
        return

    # Consumer Actions
    client.force_login(consumer)
    
    # View Home
    resp = client.get(reverse('home'))
    if 'Real Tomato' in str(resp.content):
        print_params("View Listings", True)
    else:
        print_params("View Listings", False)
        
    # Add to Cart
    resp = client.post(reverse('cart_add', args=[listing.id]), {'quantity': 2}, follow=True)
    if 'Added 2 KG' in str(list(resp.context['messages'])[0]):
        print_params("Add to Cart", True)
    else:
        print_params("Add to Cart", False)

def verify_inbox_and_messaging(farmer, consumer):
    print("\n--- 4. Inbox & Messaging ---")
    client = Client()
    
    # Send Message (Consumer -> Farmer)
    client.force_login(consumer)
    msg_body = "Is this available?"
    resp = client.post(reverse('send_message', args=[farmer.username]), {'body': msg_body}, follow=True)
    
    if resp.status_code == 200 and Message.objects.filter(sender=consumer, recipient=farmer, body=msg_body).exists():
        print_params("Send Message", True, "Message sent and persisted")
    else:
        print_params("Send Message", False, f"Failed. Status: {resp.status_code}")
        
    # Check Inbox (Farmer)
    client.force_login(farmer)
    resp = client.get(reverse('inbox'))
    if resp.status_code == 200:
        content = resp.content.decode()
        if msg_body in content:
            print_params("Inbox Access", True, "Message visible in inbox")
        else:
            print_params("Inbox Access", False, "Message NOT visible in inbox")
    else:
        print_params("Inbox Access", False, f"Failed to load inbox. Status: {resp.status_code}")

def verify_reviews(farmer, consumer):
    print("\n--- 5. Reviews ---")
    # Clean old reviews for these users
    Review.objects.filter(farmer=farmer, author=consumer).delete()
    
    Review.objects.create(farmer=farmer, author=consumer, rating=5, comment="Good")
    Review.objects.create(farmer=farmer, author=consumer, rating=4, comment="Nice")
    
    avg = Review.objects.filter(farmer=farmer).aggregate(Avg('rating'))['rating__avg']
    if avg == 4.5:
        print_params("Rating Calculation", True)
    else:
        print_params("Rating Calculation", False, f"Expected 4.5, got {avg}")

def verify_error_pages():
    print("\n--- 6. Error Pages ---")
    factory = RequestFactory()
    
    # 404
    try:
        from django.contrib.auth.models import AnonymousUser
        req = factory.get('/bad-url')
        req.session = {}
        req.user = AnonymousUser()
        resp = custom_404(req, exception=Exception("Not Found"))
        if resp.status_code == 404:
             print_params("404 Page", True)
        else:
             print_params("404 Page", False, f"Status {resp.status_code}")
    except Exception as e:
        print_params("404 Page", False, f"Error: {e}")

    # 500
    try:
        from django.contrib.auth.models import AnonymousUser
        req = factory.get('/')
        req.session = {}
        req.user = AnonymousUser()
        resp = custom_500(req)
        if resp.status_code == 500:
             print_params("500 Page", True)
        else:
             print_params("500 Page", False, f"Status {resp.status_code}")
    except Exception as e:
        print_params("500 Page", False, f"Error: {e}")

def run_all():
    print("=== STARTING FULL SYSTEM VERIFICATION ===")
    farmer, consumer = verify_auth_and_profiles()
    if farmer and consumer:
        verify_profile_enforcement(farmer, consumer)
        verify_core_features(farmer, consumer)
        verify_inbox_and_messaging(farmer, consumer)
        verify_reviews(farmer, consumer)
    verify_error_pages()
    
    # Final Cleanup
    if farmer: farmer.delete()
    if consumer: consumer.delete()
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == '__main__':
    run_all()
