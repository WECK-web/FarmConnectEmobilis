import os
import django
from django.test import Client, RequestFactory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.views import custom_500

def verify_500():
    print("\n--- Verifying Custom 500 Page ---")
    factory = RequestFactory()
    request = factory.get('/')
    request.session = {} # Mock session
    
    try:
        response = custom_500(request)
        if response.status_code == 500:
             print("✅ SUCCESS: 500 Page returns status 500")
             # Check content
             content = response.content.decode('utf-8')
             if 'ServerError' in content or '500' in content or 'Something went wrong' in content: # Adjust based on actual template
                 print("✅ SUCCESS: Content seems correct.")
             else:
                 print(f"⚠️ NOTE: Content might not match expected keywords. Content snippet: {content[:100]}")
        else:
             print(f"❌ FAILURE: Status code is {response.status_code}")
    except Exception as e:
        print(f"❌ FAILURE: Exception during rendering: {e}")

if __name__ == '__main__':
    verify_500()
