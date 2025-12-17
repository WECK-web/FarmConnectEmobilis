# Order Tracking Views

from django.utils import timezone
from .models import OrderStatusHistory

@login_required
def buyer_orders(request):
    """Display all orders for the logged-in buyer"""
    orders = Order.objects.filter(buyer=request.user).order_by('-date_ordered')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'buyer_orders.html', context)

@login_required
def order_detail(request, order_id):
    """Display detailed view of a specific order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Ensure user has permission to view this order
    if order.buyer != request.user and order.listing.seller != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('home')
    
    # Get status history
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'status_history': status_history,
        'is_farmer': order.listing.seller == request.user,
    }
    return render(request, 'order_detail.html', context)

@login_required
def farmer_orders(request):
    """Display all orders for the logged-in farmer's listings"""
    # Get all orders for this farmer's listings
    farmer_listings = Listing.objects.filter(seller=request.user)
    orders = Order.objects.filter(listing__in=farmer_listings).order_by('-date_ordered')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'farmer_orders.html', context)

@login_required
def update_order_status(request, order_id):
    """Update the status of an order (farmer only)"""
    order = get_object_or_404(Order, id=order_id)
    
    # Ensure only the farmer can update
    if order.listing.seller != request.user:
        messages.error(request, "You don't have permission to update this order.")
        return redirect('home')
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            order = form.save(commit=False)
            
            # Update timestamps based on new status
            if order.status == 'CONFIRMED' and not order.confirmed_at:
                order.confirmed_at = timezone.now()
            elif order.status == 'SHIPPED' and not order.shipped_at:
                order.shipped_at = timezone.now()
            elif order.status == 'DELIVERED' and not order.delivered_at:
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Create status history entry
            OrderStatusHistory.objects.create(
                order=order,
                status=order.status,
                changed_by=request.user,
                notes=form.cleaned_data.get('tracking_notes', '')
            )
            
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderStatusUpdateForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'update_order_status.html', context)
