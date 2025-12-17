import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

def verify_reporting():
    from django.contrib.auth.models import User
    from core.models import Report, Profile
    
    print("--- Verifying Fraud Reporting System ---")
    
    # 1. Setup
    reporter, _ = User.objects.get_or_create(username='verifier_consum', defaults={'email': 'rep@test.com'})
    if not hasattr(reporter, 'profile'): Profile.objects.create(user=reporter, user_type='CONSUMER')
    
    bad_actor, _ = User.objects.get_or_create(username='bad_farmer', defaults={'email': 'bad@test.com'})
    if not hasattr(bad_actor, 'profile'): Profile.objects.create(user=bad_actor, user_type='FARMER')
    
    admin, _ = User.objects.get_or_create(username='report_admin', defaults={'is_superuser': True, 'is_staff': True})
    
    # Clear existing reports
    Report.objects.all().delete()
    
    client = Client()
    client.force_login(reporter)
    
    # 2. Submit Report
    print(f"Submitting report against {bad_actor.username}...")
    resp = client.post(f'/report/{bad_actor.id}/', {
        'reason': 'SCAM',
        'details': 'He took my money and sent me a potato.'
    }, follow=True)
    
    if resp.status_code == 200:
        if "Report submitted" in resp.content.decode():
             print("✅ Report submitted successfully (Message verified)")
        else:
             print("❌ Report submitted but success message missing")
             
    # Verify DB
    if Report.objects.count() == 1:
        print("✅ Report found in Database")
    else:
        print(f"❌ Database Report Count: {Report.objects.count()}")
        
    # 3. Admin Review
    client.force_login(admin)
    print("Checking Admin Dashboard...")
    resp = client.get('/portal/reports/')
    content = resp.content.decode()
    
    if bad_actor.username in content and 'SCAM' in content:
        print("✅ Report visible in Admin Panel")
    else:
        print("❌ Report NOT visible in Admin Panel")
        
    # 4. Resolve Report
    if Report.objects.exists():
        rid = Report.objects.first().id
        print(f"Resolving Report #{rid}...")
        client.get(f'/portal/reports/resolve/{rid}/')
        
        r = Report.objects.first()
        if r.is_resolved:
            print("✅ Report marked as RESOLVED")
        else:
            print("❌ Report resolution failed")
            
    print("--- Verification Complete ---")

if __name__ == '__main__':
    verify_reporting()
