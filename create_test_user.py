import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

username = 'testfarmer'
password = 'testpass123'
email = 'farmer@test.com'

try:
    u = User.objects.get(username=username)
    u.delete()
    print(f"Deleted existing {username}")
except User.DoesNotExist:
    pass

u = User.objects.create_user(username=username, email=email, password=password)
p, _ = Profile.objects.get_or_create(user=u)
p.user_type = 'FARMER'
p.save()

print(f"Successfully created {username} with password {password}")
