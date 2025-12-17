
import os

path = r'c:\Users\HP\farm_project\core\views.py'

restored_code = """

@login_required
def delete_category(request, category_id):
    if not request.user.is_superuser: return redirect('home')
    Category.objects.filter(id=category_id).delete()
    return redirect('manage_categories')

@login_required
def resolve_report(request, report_id):
    if not request.user.is_superuser: return redirect('home')
    # Stub: Report model handling
    # Report.objects.filter(id=report_id).update(status='RESOLVED')
    print(f"Resolving report {report_id}")
    return redirect('manage_reports')

"""

with open(path, 'a', encoding='utf-8') as f:
    f.write(restored_code)

print("Restored final missing views.")
