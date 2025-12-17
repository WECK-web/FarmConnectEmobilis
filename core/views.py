from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.utils import timezone
from django.utils import timezone
import math
from django.db.models import Count, Sum, F






from django.contrib.auth import login, logout, authenticate



from django.contrib.auth.forms import AuthenticationForm



from django.contrib.auth.decorators import login_required



from django.contrib.auth.models import User



from django.contrib import messages



from .models import Listing, Category, Order, OrderItem, Review, Wishlist, Notification, Message, Profile, ActivityLog, Payment, Report



from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ListingForm, ReviewForm, MessageForm, MpesaPaymentForm, ReportForm, CategoryForm, AppealForm, OrderStatusUpdateForm
from django.forms import modelform_factory



from .cart import Cart



from .mpesa import MpesaClient



from django.views.decorators.http import require_POST



from django.shortcuts import get_object_or_404



from .decorators import profile_required



from django.db.models import Count, Sum, F, DecimalField, Q



from django.db.models.functions import TruncDate



import json



from django.core.serializers.json import DjangoJSONEncoder







def home(request):



    from .models import Listing, Category



    query = request.GET.get('q')



    category_id = request.GET.get('category')



    



    listings = Listing.objects.filter(is_available=True)



    



    # If user is a Farmer, hide other farmers' listings (Requirement: farmer shouldn't see other farmers listings)



    # We can either show ONLY their listings, or show NONE (if marketplace is for buying).



    # Assuming they might want to see how their listing looks, showing THEIRS is safer than empty.



    # Filter disabled to allow farmers to see all listings
    # if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':
    #     listings = listings.filter(seller=request.user)



    



    if query:



        listings = listings.filter(title__icontains=query)



    



    # Sort listings



    sort_by = request.GET.get('sort')



    if sort_by == 'price_low':



        listings = listings.order_by('price')



    elif sort_by == 'price_high':



        listings = listings.order_by('-price')



    else: # Default sorting if no specific sort is applied



        listings = listings.order_by('-created_at')



    



    if category_id:



        listings = listings.filter(category_id=category_id)



        



    



    # Get all categories for filter dropdown



    categories = Category.objects.all()



    



    # Get farmers with location for map



    farmers_with_location = User.objects.filter(



        profile__user_type='FARMER',



        profile__latitude__isnull=False,



        profile__longitude__isnull=False



    ).select_related('profile')







    context = {



        'listings': listings, 



        'categories': categories,



        'selected_category': int(category_id) if category_id else None,



        'farmers_locations': farmers_with_location



    }



    return render(request, 'home_v5.html', context)







def register(request):



    if request.method == 'POST':



        form = UserRegisterForm(request.POST)



        if form.is_valid():



            user = form.save()



            user_type = form.cleaned_data.get('user_type')



            user.profile.user_type = user_type



            user.profile.save()



            login(request, user)



            return redirect('home')



    else:



        form = UserRegisterForm()



    return render(request, 'register.html', {'form': form})







def user_login(request):



    if request.method == 'POST':



        form = AuthenticationForm(request, data=request.POST)



        if form.is_valid():



            username = form.cleaned_data.get('username')



            password = form.cleaned_data.get('password')



            user = authenticate(username=username, password=password)



            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been disabled. Please contact support.")
                    return redirect('login')
                login(request, user)



                



                # Check for 'next' parameter first



                next_url = request.GET.get('next')



                if next_url and 'login' not in next_url:



                    return redirect(next_url)



                    



                # Smart redirect based on user type



                if hasattr(user, 'profile') and user.profile.user_type == 'FARMER':



                    return redirect('farmer_dashboard')



                return redirect('home')



    else:



        form = AuthenticationForm()



        # Add bootstrap class to default auth form



        for field in form.fields.values():



            field.widget.attrs['class'] = 'form-control'



    return render(request, 'login.html', {'form': form})







def logout_view(request):



    logout(request)



    return redirect('home')







@login_required



@profile_required



def create_listing(request):



    if request.user.profile.user_type != 'FARMER':



        return redirect('home')



        



    if request.method == 'POST':



        form = ListingForm(request.POST, request.FILES)



        if form.is_valid():



            listing = form.save(commit=False)



            listing.seller = request.user



            listing.save()



            return redirect('home')



    else:



        form = ListingForm()



    return render(request, 'create_listing.html', {'form': form})







@require_POST
def cart_add(request, listing_id):
    if request.user.is_superuser:
        messages.error(request, "Administrators cannot shop on the platform.")
        return redirect('home')

    # Prevent farmers from buying (they are sellers)



    # Only Consumers can buy



    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':



        messages.error(request, 'Only consumers can purchase items.')



        return redirect('home')



        



    cart = Cart(request)



    listing = get_object_or_404(Listing, id=listing_id)



    



    # Get quantity from POST data (default to 1)



    try:



        quantity = int(request.POST.get('quantity', 1))



    except (ValueError, TypeError):



        quantity = 1



    



    # Validate quantity is positive



    if quantity <= 0:



        messages.error(request, 'Please enter a valid quantity.')



        return redirect('home')



    



    # Try to add to cart



    if cart.add(listing=listing, quantity=quantity):



        messages.success(request, f'Added {quantity} {listing.unit} of {listing.title} to cart!')



    else:



        messages.error(request, f'Cannot add {quantity} {listing.unit}. Only {listing.quantity} {listing.unit} available.')



    



    return redirect('cart_detail')







def cart_remove(request, listing_id):



    # Restrict Farmers



    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':



         return redirect('farmer_dashboard')







    cart = Cart(request)



    listing = get_object_or_404(Listing, id=listing_id)



    cart.remove(listing)



    return redirect('cart_detail')







@require_POST



def cart_update(request, listing_id):



    # Only Consumers can update cart



    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':



        return redirect('home')



    



    cart = Cart(request)



    listing = get_object_or_404(Listing, id=listing_id)



    



    # Get quantity from POST data



    try:



        quantity = int(request.POST.get('quantity', 1))



    except (ValueError, TypeError):



        messages.error(request, 'Please enter a valid quantity.')



        return redirect('cart_detail')



    



    # Validate quantity is positive



    if quantity <= 0:



        messages.error(request, 'Please enter a valid quantity.')



        return redirect('cart_detail')



    



    # Try to update cart with new quantity



    if cart.add(listing=listing, quantity=quantity, update_quantity=True):



        messages.success(request, f'Updated quantity to {quantity} {listing.unit}')



    else:



        messages.error(request, f'Cannot set quantity to {quantity}. Only {listing.quantity} {listing.unit} available.')



    



    return redirect('cart_detail')







def cart_detail(request):
    if request.user.is_superuser:
        messages.warning(request, "Administrators do not have a shopping cart.")
        return redirect('admin_dashboard')

    # Restrict Farmers



    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':



        messages.error(request, "Farmers cannot access the cart.")



        return redirect('farmer_dashboard')







    cart = Cart(request)



    return render(request, 'cart.html', {'cart': cart})







@login_required
def checkout(request):
    if request.user.is_superuser:
        messages.error(request, "Administrators cannot perform checkout.")
        return redirect('admin_dashboard')

    # Only Consumers can checkout



    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':



        return redirect('home')







    cart = Cart(request)



    form = MpesaPaymentForm()



    



    if request.method == 'POST':



        form = MpesaPaymentForm(request.POST)



        if form.is_valid():



            phone_number = form.cleaned_data['phone_number']
            location = form.cleaned_data['location']

            # Auto-save to profile if missing
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                updated = False
                if not profile.phone:
                    profile.phone = phone_number
                    updated = True
                if not profile.location:
                    profile.location = location
                    updated = True
                if updated:
                    profile.save()



            



            # Create orders for each item in the cart



            created_orders = []



            total_amount = 0



            



            for item in cart:



                listing = item['listing']



                quantity_ordered = item['quantity']



                



                # Deduct inventory



                if listing.quantity >= quantity_ordered:



                    listing.quantity -= quantity_ordered



                    if listing.quantity == 0:



                        listing.is_available = False



                    listing.save()



                    



                    # Create order



                    order = Order.objects.create(



                        listing=listing,



                        buyer=request.user,



                        status='PENDING',



                        quantity=quantity_ordered



                    )



                    created_orders.append(order)
                    
                    # Notify Seller
                    Notification.objects.create(
                        recipient=listing.seller,
                        message=f"New Order: {quantity_ordered}x {listing.title}",
                        link=f"/order/update/{order.id}/"
                    )



                    total_amount += listing.price * quantity_ordered



            



            cart.clear()



            



            if created_orders:



                # Initiate M-Pesa Payment for the first order (or bundle them? For now, let's link to the first for simplicity or create a 'Transaction' model helper. 



                # Simplification: We will link payment to the first order ID for tracking, but logically it covers the batch.



                # Ideally we need a 'Transaction' model that links to multiple orders, but let's stick to the 1-to-1 Payment-Order relationship defined or just pick the last one.



                # Better: Let's create a bundle or just just use one order for the reference. 



                



                primary_order = created_orders[0]



                client = MpesaClient()



                response = client.stk_push(phone_number, total_amount, primary_order.id)



                



                if response and 'CheckoutRequestID' in response:



                    Payment.objects.create(



                        order=primary_order,



                        checkout_request_id=response['CheckoutRequestID'],



                        phone_number=phone_number,



                        amount=total_amount,



                        status='PENDING'



                    )



                    return render(request, 'payment_pending.html', {'phone_number': phone_number, 'amount': total_amount})



                else:



                    # Fallback if STK fails (e.g. invalid auth)



                    return render(request, 'order_success.html', {'message': 'Order placed, but M-Pesa push failed. Please pay manually.'})







            return render(request, 'order_success.html')



            



    return render(request, 'checkout.html', {'cart': cart, 'form': form})







@login_required



def farmer_dashboard(request):



    # Ensure user is a farmer



    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'FARMER':



        return redirect('home')



        



    listings = Listing.objects.filter(seller=request.user)



    orders = Order.objects.filter(listing__seller=request.user).order_by('-date_ordered')



    



    total_sales = sum(order.listing.price * order.quantity for order in orders if order.status != 'CANCELLED')



    pending_orders = orders.filter(status='PENDING').count()



    



    context = {



        'listings': listings,



        'orders': orders,



        'total_sales': total_sales,



        'pending_orders': pending_orders



    }



    return render(request, 'dashboard.html', context)







def farmer_profile(request, username):



    farmer = get_object_or_404(User, username=username)



    



    # Ensure user is a farmer



    if not hasattr(farmer, 'profile') or farmer.profile.user_type != 'FARMER':



        return redirect('home')



        



    listings = Listing.objects.filter(seller=farmer, is_available=True)



    



    return render(request, 'farmer_profile.html', {'farmer': farmer, 'listings': listings})







@login_required



def send_message(request, recipient_username):



    recipient = get_object_or_404(User, username=recipient_username)



    



    if request.user == recipient:



        messages.error(request, "You cannot send a message to yourself.")



        return redirect('home')







    # Prevent Farmer -> Farmer messaging



    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':



         if hasattr(recipient, 'profile') and recipient.profile.user_type == 'FARMER':



             messages.error(request, "Farmers cannot message other farmers.")



             return redirect('home')



    



    if request.method == 'POST':



        body = request.POST.get('body')



        if body:



            Message.objects.create(sender=request.user, recipient=recipient, body=body)

            # Notify Recipient
            Notification.objects.create(
                recipient=recipient,
                message=f"New Message from {request.user.username}",
                link="/inbox/"
            )



            return redirect('inbox')



            



    return render(request, 'send_message.html', {'recipient': recipient})







@login_required



def inbox(request):



    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')



    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')



    return render(request, 'inbox.html', {'received_messages': received_messages, 'sent_messages': sent_messages})







@login_required



def update_order_status(request, order_id):



    order = get_object_or_404(Order, id=order_id)



    



    # Ensure user is the seller



    if order.listing.seller != request.user:



        return redirect('farmer_dashboard')



        



    if request.method == 'POST':



        status = request.POST.get('status')



        if status in ['PENDING', 'COMPLETED']:



            order.status = status



            order.save()



            



    return redirect('farmer_dashboard')







@login_required



def edit_listing(request, pk):



    listing = get_object_or_404(Listing, pk=pk)



    if listing.seller != request.user:



        return redirect('farmer_dashboard')



    



    if request.method == 'POST':



        form = ListingForm(request.POST, request.FILES, instance=listing)



        if form.is_valid():



            form.save()



            return redirect('farmer_dashboard')



    else:



        form = ListingForm(instance=listing)



    



    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})







@login_required



@require_POST



def delete_listing(request, pk):



    listing = get_object_or_404(Listing, pk=pk)



    if listing.seller != request.user:



        return redirect('farmer_dashboard')



    



    listing.delete()



    return redirect('farmer_dashboard')







@login_required



def consumer_orders(request):



    # Restrict Farmers



    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':



        return redirect('farmer_dashboard')







    orders = Order.objects.filter(buyer=request.user).order_by('-date_ordered')



    return render(request, 'consumer_orders.html', {'orders': orders})







@login_required



def profile(request):



    # Ensure profile exists



    if not hasattr(request.user, 'profile'):



        from .models import Profile



        Profile.objects.create(user=request.user, user_type='CONSUMER')







    if request.method == 'POST':



        u_form = UserUpdateForm(request.POST, instance=request.user)



        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)



        if u_form.is_valid() and p_form.is_valid():



            u_form.save()



            p_form.save()



            return redirect('profile')



    else:



        u_form = UserUpdateForm(instance=request.user)



        p_form = ProfileUpdateForm(instance=request.user.profile)







    context = {



        'u_form': u_form,



        'p_form': p_form



    }







    return render(request, 'profile.html', context)







from django.db.models import Avg







def user_profile_public(request, username):



    target_user = get_object_or_404(User, username=username)



    



    # Handle Review Submission



    if request.method == 'POST' and request.user.is_authenticated:



        if request.user != target_user:



            form = ReviewForm(request.POST)



            if form.is_valid():



                review = form.save(commit=False)



                review.farmer = target_user



                review.author = request.user



                review.save()



                messages.success(request, 'Review submitted successfully!')



                return redirect('user_profile_public', username=username)



        else:



            messages.error(request, 'You cannot review yourself.')







    # Get Reviews and Ratings



    reviews = Review.objects.filter(farmer=target_user).order_by('-created_at')



    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0



    review_form = ReviewForm()







    # Filter listings if Farmer



    listings = []



    if hasattr(target_user, 'profile') and target_user.profile.user_type == 'FARMER':



        listings = Listing.objects.filter(seller=target_user, is_available=True)



    



    context = {



        'target_user': target_user, 



        'listings': listings,



        'reviews': reviews,



        'avg_rating': round(avg_rating, 1),



        'review_form': review_form,



        'review_count': reviews.count()



    }



    return render(request, 'public_profile.html', context)







@login_required



@profile_required



def farmer_analytics(request):



    if request.user.profile.user_type != 'FARMER':



        return redirect('home')



        



    # 1. Revenue Trend (Daily Sales)



    daily_sales = Order.objects.filter(
        listing__seller=request.user
    ).exclude(
        status='CANCELLED'
    ).annotate(



        date=TruncDate('date_ordered')



    ).values('date').annotate(



        total_sales=Sum(F('listing__price') * F('quantity'), output_field=DecimalField())



    ).order_by('date')



    



    # 2. Top Products by Quantity Sold



    top_products = Order.objects.filter(
        listing__seller=request.user
    ).exclude(
        status='CANCELLED'
    ).values('listing__title').annotate(



        quantity_sold=Sum('quantity')



    ).order_by('-quantity_sold')[:5]



    



    # 3. Order Status Distribution



    status_dist = Order.objects.filter(



        listing__seller=request.user



    ).values('status').annotate(



        count=Count('status')



    )



    



    # 4. Sales by Category
    category_sales = Order.objects.filter(
        listing__seller=request.user
    ).exclude(
        status='CANCELLED'
    ).values('listing__category__name').annotate(
        total_revenue=Sum(F('listing__price') * F('quantity'), output_field=DecimalField())
    ).order_by('-total_revenue')

    context = {
        'daily_sales': json.dumps(list(daily_sales), cls=DjangoJSONEncoder),
        'top_products': json.dumps(list(top_products), cls=DjangoJSONEncoder),
        'status_dist': json.dumps(list(status_dist), cls=DjangoJSONEncoder),
        'category_sales': json.dumps(list(category_sales), cls=DjangoJSONEncoder),
    }



    return render(request, 'analytics.html', context)



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




# Error Handlers
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

@csrf_exempt
def mpesa_callback(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            print(f"M-Pesa Callback Received for Order {order_id}: Code {result_code}")

            payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
            if not payment:
                print(f"Payment not found for request ID: {checkout_request_id}")
                return HttpResponse("Payment Not Found", status=404)
            
            if result_code == 0:
                # Success
                metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                receipt_number = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)
                
                payment.status = 'COMPLETED'
                payment.transaction_id = receipt_number
                payment.save()
                
                order = payment.order
                order.status = 'CONFIRMED'
                order.confirmed_at = timezone.now()
                order.save()
                print(f"Payment Confirmed: {receipt_number}")
            else:
                # Failure
                payment.status = 'FAILED'
                payment.save()
                print(f"Payment Failed: {stk_callback.get('ResultDesc')}")

        except Exception as e:
            print(f"Callback Error: {e}")
            
    return HttpResponse("OK")


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
    
    orders = Order.objects.filter(listing__seller=request.user).exclude(status='CANCELLED')
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
    if not request.user.is_superuser:
        return redirect('home')
    
    users = User.objects.all()
    total_users = users.count()
    total_farmers = users.filter(profile__user_type='FARMER').count()
    total_consumers = users.filter(profile__user_type='CONSUMER').count()
    
    orders = Order.objects.all()
    total_orders = orders.count()
    pending_orders = orders.filter(status='PENDING').count()
    
    revenue = Order.objects.exclude(status='CANCELLED').aggregate(
        total=Sum(F('listing__price') * F('quantity'), output_field=DecimalField())
    )['total'] or 0
    
    recent_orders = Order.objects.select_related('buyer', 'listing__seller').order_by('-date_ordered')[:5]
    
    context = {
        'total_users': total_users,
        'total_farmers': total_farmers,
        'total_consumers': total_consumers,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': revenue,
        'recent_orders': recent_orders
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
    user = get_object_or_404(User, id=user_id)
    Notification.objects.create(recipient=user, message="Warning from Admin: Violation of terms.")
    messages.success(request, f"Warning sent to {user.username}.")
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
    reported_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.save()
            messages.success(request, f"Report submitted for {reported_user.username}.")
            return redirect('home')
    else:
        form = ReportForm()
    
    return render(request, 'report_user.html', {'form': form, 'reported_user': reported_user})


@login_required
def manage_reports(request):
    if not request.user.is_superuser: return redirect('home')
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'manage_reports.html', {'reports': reports})

@login_required
def ban_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    Notification.objects.create(recipient=user, message="Your account has been suspended by administration for violating our terms of service. Please contact support if you believe this is an error.")
    messages.success(request, f"User {user.username} has been BANNED.")
    return redirect('manage_users')

@login_required
def unban_user(request, user_id):
    if not request.user.is_superuser: return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    Notification.objects.create(recipient=user, message="Your account has been reactivated. Welcome back!")
    messages.success(request, f"User {user.username} has been UNBANNED.")
    return redirect('manage_users')



@login_required
def submit_appeal(request, user_id):
    # Stub for appeal submission
    if request.method == 'POST':
        pass 
    return redirect('home')

@login_required
def resolve_appeal(request, report_id):
    # Stub for appeal resolution
    return redirect('manage_reports')



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



@login_required
def delete_category(request, category_id):
    if not request.user.is_superuser: return redirect('home')
    Category.objects.filter(id=category_id).delete()
    return redirect('manage_categories')

@login_required
def resolve_report(request, report_id):
    if not request.user.is_superuser: return redirect('home')
    report = get_object_or_404(Report, id=report_id)
    report.is_resolved = True
    report.save()
    messages.success(request, f"Report {report.id} marked as resolved.")
    return redirect('manage_reports')

