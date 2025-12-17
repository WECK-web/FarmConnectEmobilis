
import os

path = r'c:\Users\HP\farm_project\core\views.py'

restored_code = """

# --- RESTORED VIEWS ---

import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

@login_required
def download_sales_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Order ID', 'Product', 'Quantity', 'Total Price', 'Status', 'Buyer'])
    
    orders = Order.objects.filter(listing__seller=request.user, status='COMPLETED')
    for order in orders:
        writer.writerow([
            order.date_ordered, order.id, order.listing.title, 
            order.quantity, order.total_price, order.status, order.buyer.username
        ])
    return response

@login_required
def nearby_farmers(request):
    # Basic implementation: Return all farmers for map
    # In a real impl, we'd filter by lat/lon distance
    farmers = Profile.objects.filter(user_type='FARMER').exclude(latitude__isnull=True)
    return render(request, 'nearby_farmers.html', {'farmers': farmers})

@login_required
def check_notifications(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def mark_notification_read(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return redirect('home') # Or previous page

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

@login_required
def toggle_wishlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    w_item, created = Wishlist.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        w_item.delete()
        added = False
    else:
        added = True
    return JsonResponse({'added': added})

# --- ADMIN PORTAL ---

@login_required
def admin_dashboard(request):
    if notCc request.user.is_superuser:
        return redirect('home')
    
    users_count = User.objects.count()
    orders_count = Order.objects.count()
    revenue = Order.objects.filter(status='COMPLETED').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'users_count': users_count,
        'orders_count': orders_count,
        'total_revenue': revenue
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def manage_users(request):
    if not request.user.is_superuser: return redirect('home')
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    User.objects.get(id=user_id).delete()
    return redirect('manage_users')

@login_required
def toggle_verification(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    profile = get_object_or_404(Profile, user_id=user_id)
    profile.is_verified = not profile.is_verified
    profile.save()
    return redirect('manage_users')

@login_required
def warn_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    # Placeholder: Send dummy message
    Notification.objects.create(recipient_id=user_id, message="Warning from Admin: Violation of terms.")
    return redirect('manage_users')

@login_required
def manage_listings(request):
    if not request.user.is_superuser: return redirect('home')
    listings = Listing.objects.all()
    return render(request, 'manage_listings.html', {'listings': listings})

@login_required
def manage_orders(request):
    if not request.user.is_superuser: return redirect('home')
    orders = Order.objects.all().order_by('-date_ordered')
    return render(request, 'manage_orders.html', {'orders': orders})

@login_required
def activity_logs(request):
    if not request.user.is_superuser: return redirect('home')
    logs = ActivityLog.objects.all().order_by('-timestamp')[:50]
    return render(request, 'activity_logs.html', {'logs': logs})

@login_required
def submit_report(request, user_id):
    # Any user can report
    if request.method == 'POST':
        reason = request.POST.get('reason')
        # Report model assumption: reporter, reported_user, reason
        # from .models import Report (Make sure detailed import or generic)
        # Using placeholder print for now if Model not imported, but Report should be in .models
        pass
    return redirect('home')

@login_required
def manage_reports(request):
    if not request.user.is_superuser: return redirect('home')
    return render(request, 'manage_reports.html')

@login_required
def ban_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('manage_users')

@login_required
def unban_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('manage_users')

"""

with open(path, 'a', encoding='utf-8') as f:
    f.write(restored_code)

print("Restored missing views.")
