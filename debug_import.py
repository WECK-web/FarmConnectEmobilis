import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect.settings')
django.setup()

print("Django setup complete.")
try:
    print("DEBUG: Importing core.forms...")
    try:
        from core import forms
        print("SUCCESS: imported core.forms")
    except ImportError as e:
        print(f"FAILED to import core.forms: {e}")
        raise e
    
except ImportError as e:
    import traceback
    traceback.print_exc()
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed to import Report: {e}")
except Exception as e:
    print(f"Other error: {e}")
