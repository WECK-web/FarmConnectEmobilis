import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Notification, Profile

# Create demo users if they don't exist
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@farmconnect.com',
        'is_superuser': True,
        'is_staff': True
    }
)
admin_user.set_password('admin123')
admin_user.save()

demo_user, _ = User.objects.get_or_create(
    username='demouser',
    defaults={'email': 'demo@example.com'}
)
demo_user.set_password('demo123')
demo_user.is_active = True
demo_user.save()

# Clear old notifications for clean demo
Notification.objects.filter(recipient=demo_user).delete()

print("Setup complete!")
print(f"Admin user: {admin_user.username} (password: admin123)")
print(f"Demo user: {demo_user.username} (password: demo123)")
print(f"Demo user is active: {demo_user.is_active}")
print("\nYou can now:")
print("1. Login as admin at: http://localhost:8000/login/")
print("2. Go to: http://localhost:8000/portal/users/")
print("3. Test Ban/Warn/Unban on 'demouser'")
