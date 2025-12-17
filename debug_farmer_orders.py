
import os
import django
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context, Template
from django.http import HttpRequest
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.models import Order, Listing, User, Profile

try:
    # Create dummy request and user
    user = User.objects.first()
    if not user:
        print("No users found to test with.")
        exit()
        
    request = HttpRequest()
    request.user = user
    
    # Try to render the template
    # We mock the context
    context = {
        'orders': [],
        'status_filter': None
    }
    
    rendered = render_to_string('farmer_orders.html', context, request=request)
    print("SUCCESS: Template rendered successfully.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
