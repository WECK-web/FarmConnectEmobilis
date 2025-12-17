
import os

path = r"c:\Users\HP\farm_project\templates\home_v5.html"
try:
    with open(path, "r", encoding='utf-8') as f:
        content = f.read()
    
    if "cat.id==selected_category" in content:
        print("Found incorrect syntax. Fixing...")
        new_content = content.replace("cat.id==selected_category", "cat.id == selected_category")
        with open(path, "w", encoding='utf-8') as f:
            f.write(new_content)
        print("File updated successfully.")
    else:
        print("Incorrect syntax NOT found. File might be already fixed?")
        
    # Verify
    with open(path, "r", encoding='utf-8') as f:
        final_content = f.read()
        if "cat.id == selected_category" in final_content:
             print("VERIFICATION: SUCCESS - Found correct syntax.")
        else:
             print("VERIFICATION: FAILED - Correct syntax missing.")

except Exception as e:
    print(f"Error: {e}")
