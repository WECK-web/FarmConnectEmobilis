import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Notification, Message, Profile
from django.test import Client

def simulate_notifications():
    print("--- Simulating Notifications ---")
    
    # 1. Setup Users
    sender, _ = User.objects.get_or_create(username='notif_sender')
    recipient, _ = User.objects.get_or_create(username='notif_recipient')
    recipient.set_password('pass')
    recipient.save()
    Profile.objects.update_or_create(user=recipient, defaults={'user_type': 'CONSUMER'})

    client = Client()
    client.force_login(recipient)
    
    # 2. Clear previous notifications
    Notification.objects.filter(recipient=recipient).delete()
    
    # 3. Trigger Notification (Simulate Message Send logic manually or via view if possible)
    # Using View is better but complicated with redirects. Let's create object directly to test API,
    # AND create object via Message View to test integration.
    
    print("\n[TEST 1] Manual Object Creation & API Check")
    notify = Notification.objects.create(recipient=recipient, message="Test Notif 1", link="/test")
    
    resp = client.get('/api/notifications/check/')
    data = resp.json()
    
    if data['count'] == 1 and data['notifications'][0]['message'] == "Test Notif 1":
        print("✅ API returned correct count and message")
    else:
        print(f"❌ API Failed: {data}")
        
    # 4. Mark Read
    print("\n[TEST 2] Mark Read Endpoint")
    resp = client.get(f'/notifications/read/{notify.id}/', follow=True)
    
    notify.refresh_from_db()
    if notify.is_read:
        print("✅ Notification marked read")
    else:
        print("❌ Notification NOT marked read")
        
    # 5. Check API again (Count Should be 0)
    resp = client.get('/api/notifications/check/')
    data = resp.json()
    if data['count'] == 0:
         print("✅ Count dropped to 0")
    else:
         print(f"❌ Count is {data['count']}, expected 0")

    print("\n--- Notification Simulation Complete ---")

if __name__ == '__main__':
    simulate_notifications()
