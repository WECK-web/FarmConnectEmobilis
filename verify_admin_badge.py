import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User

def verify_admin_badge():
    print("--- Verifying Admin Badge ---")
    
    # 1. Setup Admin
    admin, _ = User.objects.get_or_create(username='badge_admin', defaults={'is_superuser': True, 'email': 'admin@test.com'})
    client = Client()
    client.force_login(admin)
    
    # 2. Check Profile Page
    resp = client.get('/profile/')
    content = resp.content.decode()
    
    if 'Administrator' in content and 'bg-danger' in content:
        print("✅ Admin Badge found (Administrator)")
    else:
        print("❌ Admin Badge NOT found")
        # Print snippet
        idx = content.find(admin.username)
        print(content[idx:idx+300])
        
    # 3. Check Consumer (Should NOT see Admin badge)
    consumer, _ = User.objects.get_or_create(username='badge_consumer')
    client.force_login(consumer)
    resp = client.get('/profile/')
    content = resp.content.decode()
    
    if 'Administrator' not in content:
        print("✅ Consumer properly sees normal badge")
    else:
        print("❌ Consumer SEES Admin badge (Error)")

if __name__ == '__main__':
    verify_admin_badge()
