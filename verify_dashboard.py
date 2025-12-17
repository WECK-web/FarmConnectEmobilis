import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User

def verify_dashboard():
    print("--- Verifying Dashboard Buttons ---")
    
    # 1. Setup Superuser
    admin, _ = User.objects.get_or_create(username='dash_admin', defaults={'is_superuser': True, 'is_staff': True})
    admin.set_password('pass')
    admin.save()
    
    client = Client()
    client.force_login(admin)
    
    # 2. Get Dashboard
    resp = client.get('/portal/dashboard/')
    content = resp.content.decode()
    
    # 3. Check for specific text
    if 'Manage Users' in content:
        print("✅ 'Manage Users' button found")
    else:
        print("❌ 'Manage Users' button NOT found")
        # Print snippet where it should be
        idx = content.find('Administrator Dashboard')
        print(content[idx:idx+500])

if __name__ == '__main__':
    verify_dashboard()
