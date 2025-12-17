import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

# 1. Cleaner Admin
admin, _ = User.objects.get_or_create(username='admin_clean')
admin.set_password('cleanpass123')
admin.is_superuser = True
admin.is_staff = True
admin.save()
if not hasattr(admin, 'profile'):
    Profile.objects.create(user=admin, user_type='FARMER')
print(f"Admin Ready: {admin.username}")

# 2. Cleaner Victim
victim, _ = User.objects.get_or_create(username='victim_clean')
victim.set_password('victimpass123')
victim.email = 'victim@test.com'
victim.is_active = True # START ACTIVE
victim.save()
if not hasattr(victim, 'profile'):
    Profile.objects.create(user=victim, user_type='CONSUMER')
print(f"Victim Ready: {victim.username} (Active={victim.is_active})")
