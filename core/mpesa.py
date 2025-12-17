import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaClient:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.base_url = settings.MPESA_BASE_URL
        self.callback_url = settings.MPESA_CALLBACK_URL

    def get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = (self.consumer_key, self.consumer_secret)
        try:
            response = requests.get(url, auth=auth)
            print(f"DEBUG: Auth Status: {response.status_code}") # DEBUG
            print(f"DEBUG: Auth Response: {response.text}") # DEBUG
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    def stk_push(self, phone_number, amount, order_id):
        access_token = self.get_access_token()
        if not access_token:
            print("DEBUG: No Access Token retrieved.") # DEBUG
            return None

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode('utf-8')
        
        # Ensure phone format (254...)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]
        
        print(f"DEBUG: Initiating STK Push to {phone_number} for {amount}") # DEBUG
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount), 
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{self.callback_url}{order_id}/", 
            "AccountReference": f"Order-{order_id}",
            "TransactionDesc": f"Payment for Order {order_id}"
        }

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"DEBUG: STK Push Status: {response.status_code}") # DEBUG
            print(f"DEBUG: STK Push Response: {response.text}") # DEBUG
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error initiating STK Push: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return None
