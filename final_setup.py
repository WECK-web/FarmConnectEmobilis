import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Notification

# 1. DELETE and RECREATE admin to be 100% sure
try:
    old_admin = User.objects.get(username='admin')
    old_admin.delete()
    print("Deleted old admin user")
except User.DoesNotExist:
    pass

admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print(f"Created FRESH admin user: {admin.username} / admin123")
print(f"Is active: {admin.is_active}")
print(f"Is superuser: {admin.is_superuser}")
print(f"Is staff: {admin.is_staff}")

# 2. Setup demo user
try:
    demo = User.objects.get(username='demouser')
    demo.delete()
    print("Deleted old demouser")
except User.DoesNotExist:
    pass

demo = User.objects.create_user('demouser', 'demo@example.com', 'password123')
demo.is_active = True
demo.save()
print(f"Created FRESH demo user: {demo.username}")

# Clear notifications
Notification.objects.all().delete()
print("Cleared all notifications")
