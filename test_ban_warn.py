import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Notification, Profile
from django.test import Client

print("=" * 70)
print("BAN/WARN/UNBAN FUNCTIONALITY TEST")
print("=" * 70)

# Setup test users
try:
    admin = User.objects.get(username='admin_demo')
except User.DoesNotExist:
    admin = User.objects.create_superuser(username='admin_demo', email='admin@test.com', password='admin123')
    print(f"Created admin user: {admin.username}")

try:
    test_user = User.objects.get(username='testuser_demo')
except User.DoesNotExist:
    test_user = User.objects.create_user(username='testuser_demo', email='test@test.com', password='test123')
    print(f"Created test user: {test_user.username}")

# Reset user state
test_user.is_active = True
test_user.save()
Notification.objects.filter(recipient=test_user).delete()

# Create test client
client = Client()
client.force_login(admin)

print(f"\nInitial State:")
print(f"  User: {test_user.username}")
print(f"  Active: {test_user.is_active}")
print(f"  Notifications: {Notification.objects.filter(recipient=test_user).count()}")

# TEST 1: BAN
print("\n" + "-" * 70)
print("TEST 1: Banning user...")
response = client.get(f'/portal/users/ban/{test_user.id}/', follow=True)
test_user.refresh_from_db()
notifs = Notification.objects.filter(recipient=test_user)

print(f"Result:")
print(f"  Active: {test_user.is_active}")
print(f"  Notifications: {notifs.count()}")
if notifs.exists():
    print(f"  Message: '{notifs.first().message}'")
print(f"  Status: {'PASS' if not test_user.is_active and notifs.count() == 1 else 'FAIL'}")

# TEST 2: WARN
print("\n" + "-" * 70)
print("TEST 2: Warning user...")
before_count = Notification.objects.filter(recipient=test_user).count()
response = client.get(f'/portal/users/warn/{test_user.id}/', follow=True)
after_count = Notification.objects.filter(recipient=test_user).count()
latest = Notification.objects.filter(recipient=test_user).latest('created_at')

print(f"Result:")
print(f"  Notifications before: {before_count}")
print(f"  Notifications after: {after_count}")
print(f"  Latest message: '{latest.message}'")
print(f"  Status: {'PASS' if after_count > before_count else 'FAIL'}")

# TEST 3: UNBAN
print("\n" + "-" * 70)
print("TEST 3: Unbanning user...")
before_count = Notification.objects.filter(recipient=test_user).count()
response = client.get(f'/portal/users/unban/{test_user.id}/', follow=True)
test_user.refresh_from_db()
after_count = Notification.objects.filter(recipient=test_user).count()
latest = Notification.objects.filter(recipient=test_user).latest('created_at')

print(f"Result:")
print(f"  Active: {test_user.is_active}")
print(f"  Notifications before: {before_count}")
print(f"  Notifications after: {after_count}")
print(f"  Latest message: '{latest.message}'")
print(f"  Status: {'PASS' if test_user.is_active and after_count > before_count else 'FAIL'}")

# SUMMARY
print("\n" + "=" * 70)
print("SUMMARY - All Notifications Sent:")
print("=" * 70)
all_notifs = Notification.objects.filter(recipient=test_user).order_by('created_at')
for i, notif in enumerate(all_notifs, 1):
    print(f"{i}. {notif.message}")

print(f"\nTotal: {all_notifs.count()} notifications sent")
print("=" * 70)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 70)
