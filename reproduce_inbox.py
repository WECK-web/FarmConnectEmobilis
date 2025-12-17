import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Message

def reproduce_inbox_issue():
    print("--- Reproducing Inbox Issue ---")
    client = Client()
    
    # Create Users
    sender, _ = User.objects.get_or_create(username='sender_user')
    sender.set_password('pass')
    sender.save()
    recipient, _ = User.objects.get_or_create(username='recipient_user')
    recipient.set_password('pass')
    recipient.save()
    
    # Create Message
    Message.objects.create(sender=sender, recipient=recipient, body="Hello World")
    
    # specific fix for profiles to pass profile_required if necessary (though inbox is just login_required)
    from core.models import Profile
    # Ensure they have profiles just in case
    # Profile.objects.get_or_create(user=sender)
    
    # Login as recipient
    client.force_login(recipient)
    
    print("Accessing Inbox...")
    try:
        response = client.get(reverse('inbox'))
        if response.status_code == 200:
            print("[SUCCESS] Inbox accessed successfully.")
            if "Hello World" in response.content.decode():
                print("[SUCCESS] Message content found.")
            else:
                print("[FAILURE] Message content NOT found in inbox.")
        else:
            print(f"[FAILURE] Inbox access failed with status: {response.status_code}")
    except Exception as e:
        print(f"[FAILURE] Exception accessing inbox: {e}")

    # Test Sending Mechanism
    print("\nAccessing Send Message...")
    client.force_login(sender)
    try:
        resp = client.post(reverse('send_message', args=[recipient.username]), {'body': 'New Msg'})
        if resp.status_code == 302: # Redirect to inbox
             print("[SUCCESS] Send Message redirected (likely success).")
        else:
             print(f"[FAILURE] Send Message failed/not redirected. Status: {resp.status_code}")
    except Exception as e:
        print(f"[FAILURE] Exception sending message: {e}")

if __name__ == '__main__':
    reproduce_inbox_issue()
