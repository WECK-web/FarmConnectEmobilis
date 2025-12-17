
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.forms import OrderStatusUpdateForm
from core.models import Order, Listing, Profile, Category
from django.contrib.auth.models import User
from django.utils import timezone

# Create dummy order context if needed (ModelForm needs instance usually?)
# But we can test unbound form or bound form.
# We want to test bound form with POST data.

data = {'status': 'CONFIRMED'}
# Missing 'tracking_notes', 'estimated_delivery'

form = OrderStatusUpdateForm(data=data)

if form.is_valid():
    print("Form is VALID with just status.")
else:
    print("Form is INVALID.")
    print(form.errors)
