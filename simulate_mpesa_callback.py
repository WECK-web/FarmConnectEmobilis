import os
import django
import requests
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Order, Listing, Payment, Profile

def simulate_callback():
    print("--- Simulating M-Pesa Callback ---")
    
    # 1. Setup Data
    user, _ = User.objects.get_or_create(username='callback_tester')
    seller, _ = User.objects.get_or_create(username='seller_tester')
    Profile.objects.update_or_create(user=seller, defaults={'user_type': 'FARMER'})
    
    listing = Listing.objects.create(seller=seller, title="Callback Item", price=100, quantity=10, expiry_date='2025-12-31')
    order = Order.objects.create(buyer=user, listing=listing, quantity=1, status='PENDING')
    
    req_id = f"ws_CO_DMZ_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    payment = Payment.objects.create(
        order=order,
        checkout_request_id=req_id,
        phone_number="254700000000",
        amount=100,
        status='PENDING'
    )
    
    print(f"Created Payment {payment.id} with RequestID: {req_id}")
    
    # 2. Prepare Payload
    payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620542-1",
                "CheckoutRequestID": req_id,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100.00},
                        {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                        {"Name": "TransactionDate", "Value": 20191219102115},
                        {"Name": "PhoneNumber", "Value": 254708374149}
                    ]
                }
            }
        }
    }
    
    # 3. Send Request
    url = f"http://127.0.0.1:8000/api/mpesa/callback/{order.id}/"
    print(f"Sending Callback to: {url}")
    
    try:
        resp = requests.post(url, json=payload)
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
        # 4. Verify DB
        payment.refresh_from_db()
        order.refresh_from_db()
        
        if payment.status == 'COMPLETED' and payment.transaction_id == 'NLJ7RT61SV':
            print("✅ Payment Marked COMPLETED")
        else:
            print(f"❌ Payment Status: {payment.status}")
            
        if order.status == 'CONFIRMED' and order.confirmed_at:
            print("✅ Order Marked CONFIRMED")
        else:
            print(f"❌ Order Status: {order.status}")
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

if __name__ == '__main__':
    simulate_callback()
