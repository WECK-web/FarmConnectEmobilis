import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Message

def simulate_conversation():
    print("\n--- Simulating User Conversation ---")
    client = Client()

    # Create Users
    alice = User.objects.create_user(username='alice', password='password123')
    bob = User.objects.create_user(username='bob', password='password123')
    
    # 1. Alice sends message to Bob
    print("\n1. Alice logs in and sends message to Bob...")
    client.force_login(alice)
    response = client.post(reverse('send_message', args=['bob']), {'body': 'Hi Bob, are your tomatoes fresh?'})
    
    if response.status_code == 302:
        print("   [SUCCESS] Message sent! Redirected to inbox.")
    else:
        print(f"   [FAILURE] Failed to send message. Status: {response.status_code}")

    # 2. Bob checks inbox
    print("\n2. Bob logs in and checks inbox...")
    client.force_login(bob)
    response = client.get(reverse('inbox'))
    content = response.content.decode()
    
    if 'Hi Bob, are your tomatoes fresh?' in content:
        print("   [SUCCESS] Bob received the message.")
    else:
        print("   [FAILURE] Message not found in Bob's inbox.")

    # 3. Bob replies
    print("\n3. Bob replies to Alice...")
    # Ideally Bob clicks 'Reply' which goes to send_message view
    response = client.post(reverse('send_message', args=['alice']), {'body': 'Yes Alice, picked this morning!'})
    if response.status_code == 302:
        print("   [SUCCESS] Reply sent!")
    
    # 4. Alice checks inbox
    print("\n4. Alice checks inbox...")
    client.force_login(alice)
    response = client.get(reverse('inbox'))
    content = response.content.decode()
    
    if 'Yes Alice, picked this morning!' in content:
        print("   [SUCCESS] Alice received the reply.")
    else:
        print("   [FAILURE] Reply not found in Alice's inbox.")

    # Show Database State
    print("\n--- Database Content ---")
    msgs = Message.objects.all().order_by('timestamp')
    for m in msgs:
        print(f"[{m.timestamp.strftime('%H:%M:%S')}] {m.sender} -> {m.recipient}: {m.body}")

    # Cleanup
    alice.delete()
    bob.delete()

if __name__ == '__main__':
    simulate_conversation()
