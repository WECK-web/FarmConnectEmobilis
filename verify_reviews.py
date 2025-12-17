
import os
import django
from django.db.models import Avg

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Review, Profile

def verify_reviews():
    print("Verifying Reviews...")

    # 1. Setup Data
    # Cleanup
    if User.objects.filter(username='farmer_review_test').exists():
        User.objects.get(username='farmer_review_test').delete()
    if User.objects.filter(username='buyer_review_test').exists():
        User.objects.get(username='buyer_review_test').delete()

    farmer = User.objects.create_user(username='farmer_review_test', password='password')
    farmer.profile.user_type = 'FARMER'
    farmer.profile.save()
    
    buyer = User.objects.create_user(username='buyer_review_test', password='password')
    buyer.profile.user_type = 'CONSUMER'
    buyer.profile.save()
    
    # 2. Create Reviews
    Review.objects.create(farmer=farmer, author=buyer, rating=5, comment="Great!")
    Review.objects.create(farmer=farmer, author=buyer, rating=3, comment="Okay.")

    # 3. Check Ratings
    avg_rating = Review.objects.filter(farmer=farmer).aggregate(Avg('rating'))['rating__avg']
    print(f"Average Rating: {avg_rating}") # Expect 4.0
    
    if avg_rating == 4.0:
        print("SUCCESS: Average rating calculation is correct.")
    else:
        print(f"FAILURE: Expected 4.0, got {avg_rating}")

    # Cleanup
    # User.objects.get(username='farmer_review_test').delete()
    # User.objects.get(username='buyer_review_test').delete()

if __name__ == '__main__':
    verify_reviews()
