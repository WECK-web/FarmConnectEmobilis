
import os

path = r'c:\Users\HP\farm_project\core\views.py'

restored_code = """

@login_required
def manage_categories(request):
    if not request.user.is_superuser: return redirect('home')
    categories = Category.objects.all()
    # Stub for adding/deleting logic if POST
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
        elif 'delete' in request.POST:
            cat_id = request.POST.get('category_id')
            Category.objects.filter(id=cat_id).delete()
        return redirect('manage_categories')
    return render(request, 'manage_categories.html', {'categories': categories})

"""

with open(path, 'a', encoding='utf-8') as f:
    f.write(restored_code)

print("Restored manage_categories view.")
