
import os
import django
from django.template.loader import render_to_string
from django.conf import settings

# Setup Django standalone (minimal)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

def test_render():
    print("--- START HOME TEMPLATE RENDER TEST ---")
    try:
        # Mock Context
        class MockCat:
            id = 1
            name = "Veg"
            
        context = {
            'categories': [MockCat()],
            'selected_category': 1,
            'listings': [],
            'farmers_with_location': [],
            'request': None # Simpler than mocking full request
        }
        
        # Test 1: home_v5.html (The one we fixed)
        print("Testing home_v5.html...")
        try:
            rendered = render_to_string('home_v5.html', context)
            if "value=\"1\" selected" in rendered:
                 print("SUCCESS: home_v5.html rendered and logic worked (Has spaces).")
            else:
                 print("WARNING: Rendered but didn't find 'selected'. Logic might be off, but syntax is OK.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"FAILURE: home_v5.html crashed: {e}")

        # Test 2: home.html (Just in case)
        print("Testing home.html...")
        try:
            rendered = render_to_string('home.html', context)
            print("SUCCESS: home.html rendered cleanly.")
        except Exception as e:
            print(f"FAILURE: home.html crashed: {e}")

    except Exception as e:
        print(f"CRITICAL SETUP ERROR: {e}")

if __name__ == "__main__":
    test_render()
