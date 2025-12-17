import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Notification, Profile

print("Verifying Admin Actions (Ban/Warn/Unban)...")
print("=" * 60)

# 1. Setup Data - Use get or create more carefully
try:
    admin = User.objects.get(username='admin_test_ban')
except User.DoesNotExist:
    admin = User.objects.create_user(username='admin_test_ban', password='test123')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()

try:
    target_user = User.objects.get(username='bad_user_test')
except User.DoesNotExist:
    target_user = User.objects.create_user(username='bad_user_test', password='test123')

# Ensure user is active initially
target_user.is_active = True
target_user.save()

# Clear previous notifications
Notification.objects.filter(recipient=target_user).delete()

# 2. Test using Django test client
from django.test import Client
client = Client()
client.force_login(admin)

print(f"\nTarget user: {target_user.username}")
print(f"Initial status: Active={target_user.is_active}")
print(f"Initial notifications: {Notification.objects.filter(recipient=target_user).count()}")

# Test BAN
print("\n" + "=" * 60)
print("Testing BAN...")
response = client.get(f'/portal/users/ban/{target_user.id}/', follow=True)
target_user.refresh_from_db()
ban_notif_count = Notification.objects.filter(recipient=target_user).count()

print(f"After BAN: Active={target_user.is_active}, Notifications={ban_notif_count}")

if not target_user.is_active and ban_notif_count == 1:
    notif = Notification.objects.filter(recipient=target_user).first()
    print(f"Notification message: '{notif.message[:60]}...'")
    print("✅ BAN SUCCESS (User banned + notification sent)")
else:
    print(f"❌ BAN FAILED (Active={target_user.is_active}, Notifs={ban_notif_count})")

# Test WARN
print("\n" + "=" * 60)
print("Testing WARN...")
initial_notifs = Notification.objects.filter(recipient=target_user).count()
response = client.get(f'/portal/users/warn/{target_user.id}/', follow=True)
final_notifs = Notification.objects.filter(recipient=target_user).count()

print(f"Notifications: {initial_notifs} -> {final_notifs}")

if final_notifs > initial_notifs:
    latest_notif = Notification.objects.filter(recipient=target_user).latest('created_at')
    print(f"Latest notification: '{latest_notif.message}'")
    print("✅ WARN SUCCESS")
else:
    print("❌ WARN FAILED")

# Test UNBAN
print("\n" + "=" * 60)
print("Testing UNBAN...")
notifs_before = Notification.objects.filter(recipient=target_user).count()
response = client.get(f'/portal/users/unban/{target_user.id}/', follow=True)
target_user.refresh_from_db()
notifs_after = Notification.objects.filter(recipient=target_user).count()

print(f"After UNBAN: Active={target_user.is_active}")
print(f"Notifications: {notifs_before} -> {notifs_after}")

if target_user.is_active and notifs_after > notifs_before:
    latest_notif = Notification.objects.filter(recipient=target_user).latest('created_at')
    print(f"Latest notification: '{latest_notif.message}'")
    print("✅ UNBAN SUCCESS (User unbanned + notification sent)")
else:
    print(f"❌ UNBAN FAILED (Active={target_user.is_active}, Notif increase={notifs_after > notifs_before})")

# Summary
print("\n" + "=" * 60)
print("FINAL SUMMARY:")
all_notifs = Notification.objects.filter(recipient=target_user).order_by('created_at')
print(f"Total notifications sent to {target_user.username}: {all_notifs.count()}")
for i, notif in enumerate(all_notifs, 1):
    print(f"  {i}. {notif.message[:70]}...")

print("\n" + "=" * 60)
print("All tests completed!")
