from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Listing, Category, Order, Message
from .forms import ListingForm, UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from .cart import Cart
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

def home(request):
    from .models import Listing, Category
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    
    listings = Listing.objects.filter(is_available=True)
    
    if query:
        listings = listings.filter(title__icontains=query)
    if category_id:
        listings = listings.filter(category_id=category_id)
        
    listings = listings.order_by('-created_at')
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    try:
        selected_category = int(category_id) if category_id else None
    except ValueError:
        selected_category = None
    
    return render(request, 'home_new.html', {'listings': listings, 'categories': categories, 'selected_category': selected_category})

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
    # Prevent farmers from buying (they are sellers)
    # Only Consumers can buy
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':
        return redirect('home')
        
    cart = Cart(request)
    listing = get_object_or_404(Listing, id=listing_id)
    cart.add(listing=listing)
    return redirect('cart_detail')

def cart_remove(request, listing_id):
    cart = Cart(request)
    listing = get_object_or_404(Listing, id=listing_id)
    cart.remove(listing)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def checkout(request):
    # Only Consumers can checkout
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':
        return redirect('home')

    cart = Cart(request)
    if request.method == 'POST':
        # Create orders for each item in the cart
        for item in cart:
            listing = item['listing']
            quantity_ordered = item['quantity']
            
            # Deduct inventory
            if listing.quantity >= quantity_ordered:
                listing.quantity -= quantity_ordered
                
                # Mark as unavailable if sold out
                if listing.quantity == 0:
                    listing.is_available = False
                    
                listing.save()
                
                # Create order
                Order.objects.create(
                    listing=listing,
                    buyer=request.user,
                    status='PENDING'
                )
            # If insufficient stock, skip this item (or handle error)
            
        cart.clear()
        return render(request, 'order_success.html')
    return render(request, 'checkout.html', {'cart': cart})

@login_required
def farmer_dashboard(request):
    # Ensure user is a farmer
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'FARMER':
        return redirect('home')
        
    listings = Listing.objects.filter(seller=request.user)
    orders = Order.objects.filter(listing__seller=request.user).order_by('-date_ordered')
    
    total_sales = sum(order.listing.price for order in orders if order.status == 'COMPLETED')
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
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(sender=request.user, recipient=recipient, body=body)
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
