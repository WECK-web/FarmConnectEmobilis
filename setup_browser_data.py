from django.contrib.auth.models import User
from core.models import Profile, Listing, Category

print("--- Seeding Browser Demo Data ---")

# 1. Consumer
consumer, _ = User.objects.get_or_create(username='demo_consumer', email='consumer@demo.com')
consumer.set_password('password123')
consumer.save()
if not hasattr(consumer, 'profile'): Profile.objects.create(user=consumer, user_type='CONSUMER')
print("✅ Consumer: demo_consumer / password123")

# 2. Bad Farmer
farmer, _ = User.objects.get_or_create(username='bad_farmer', email='bad@demo.com')
farmer.set_password('password123')
farmer.save()
if not hasattr(farmer, 'profile'): Profile.objects.create(user=farmer, user_type='FARMER', is_verified=True)

# Create Listing for Farmer
cat, _ = Category.objects.get_or_create(name='Vegetables')
listing, _ = Listing.objects.get_or_create(
    seller=farmer, 
    title='Suspicious Carrots', 
    defaults={
        'category': cat,
        'description': 'Very shiny carrots.',
        'quantity': 100,
        'price': 50.00,
        'expiry_date': '2025-12-31'
    }
)
print(f"✅ Farmer: bad_farmer / password123 (Listing: {listing.title})")

# 3. Admin
admin, _ = User.objects.get_or_create(username='demo_admin', email='admin@demo.com')
admin.set_password('password123')
admin.is_superuser = True
admin.is_staff = True
admin.save()
if not hasattr(admin, 'profile'): Profile.objects.create(user=admin, user_type='CONSUMER')
print("✅ Admin: demo_admin / password123")

print("--- Seeding Complete ---")
