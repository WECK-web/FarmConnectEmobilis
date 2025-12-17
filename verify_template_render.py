
import os
import django
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

from core.models import Order, Listing, User, Category

def test_render():
    print("--- START RENDERING TEST ---")
    try:
        # Create dummy context (mocking objects)
        class MockUser:
            username = "TestBuyer"
        
        class MockProfile:
            user_type = "DEMO"
            is_verified = True

        class MockCategory:
            name = "TestCategory"

        class MockListing:
            title = "Test Listing Item"
            price = 100.00
            unit = "kg"
            category = MockCategory()
            seller = MockUser() # Needed?
            
        class MockOrder:
            id = 999
            quantity = 5
            date_ordered = datetime(2025, 12, 25, 10, 0, 0)
            status = 'PENDING'
            listing = MockListing()
            get_status_display = "Pending"
            
        mock_orders = [MockOrder()]
        
        context = {
            'orders': mock_orders,
            'status_filter': None
        }
        
        # Render the specific block or part we care about? 
        # Let's just try to render the whole thing and grep the date.
        rendered = render_to_string('buyer_orders.html', context)
        print("--- RENDERED OUTPUT START ---")
        print(rendered)
        print("--- RENDERED OUTPUT END ---")
        
        if "Dec 25, 2025" in rendered:
            print("SUCCESS: Date rendered correctly as 'Dec 25, 2025'")
            print("Snippet found:")
            # Find the line
            lines = rendered.split('\n')
            for line in lines:
                if "Dec 25, 2025" in line:
                    print(line.strip())
        else:
            print("FAILURE: Date not found in output!")
            print("Searching for curly braces...")
            if "{{" in rendered:
                print("CRITICAL FAILURE: Found '{{' in rendered output!")
            else:
                print("Output does not contain date but also no curly braces.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_render()
