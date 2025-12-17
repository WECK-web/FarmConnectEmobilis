
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.mpesa import MpesaClient

def test_mpesa_push():
    print("Testing M-Pesa Integration...")
    client = MpesaClient()
    
    # Test Auth
    print("1. Testing Authentication...")
    token = client.get_access_token()
    if token:
        print(f"SUCCESS: Got Access Token: {token[:10]}...")
    else:
        print("FAILURE: Could not get Access Token. Check Credentials.")
        return

    # Test STK Push (if verify_number provided)
    if len(sys.argv) > 1:
        phone = sys.argv[1]
        print(f"2. Testing STK Push to {phone}...")
        res = client.stk_push(phone, 1, 12345) # Amount 1, Order 12345
        if res:
            print(f"Response: {res}")
        else:
            print("FAILURE: STK Push failed.")
    else:
        print("Skipping STK Push (No phone provided). Run: python test_mpesa_script.py <phone>")

if __name__ == '__main__':
    test_mpesa_push()
