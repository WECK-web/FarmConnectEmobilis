import shutil
import os
import time

def clean():
    path = "c:\\Users\\HP\\farm_project\\core\\__pycache__"
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Cleaned {path}")
        except Exception as e:
            print(f"Failed to clean {path}: {e}")
    else:
        print("No pycache found there.")
        
    # Touch forms.py
    forms_path = "c:\\Users\\HP\\farm_project\\core\\forms.py"
    if os.path.exists(forms_path):
        os.utime(forms_path, None)
        print("Touched forms.py")

if __name__ == '__main__':
    clean()
