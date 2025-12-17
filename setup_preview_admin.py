import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from django.contrib.auth.models import User

# Create dedicated admin for preview
u, created = User.objects.get_or_create(username='admin_preview', defaults={'email': 'admin@test.com'})
u.set_password('previewpass')
u.is_superuser = True
u.is_staff = True
u.save()
print("Created/Updated 'admin_preview' with password 'previewpass'.")

# Ensure a target user exists
target, _ = User.objects.get_or_create(username='target_user')
target.set_password('targetpass')
target.save()
print("Ensured 'target_user' exists.")
