from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Profile, Listing, Order, Review, Payment
from .forms import ListingForm, UserRegisterForm, ProfileUpdateForm, ReviewForm, MpesaPaymentForm
from .cart import Cart
from .mpesa import MpesaClient
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .decorators import profile_required
from django.db.models import Count, Sum, F, DecimalField
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
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':
        listings = listings.filter(seller=request.user)
    
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
    return render(request, 'home_v2.html', context)

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
@profile_required
def cart_add(request, listing_id):
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
    # Restrict Farmers
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'FARMER':
        messages.error(request, "Farmers cannot access the cart.")
        return redirect('farmer_dashboard')

    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

@login_required
@profile_required
def checkout(request):
    # Only Consumers can checkout
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'CONSUMER':
        return redirect('home')

    cart = Cart(request)
    form = MpesaPaymentForm()
    
    if request.method == 'POST':
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            
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
    
    total_sales = sum(order.listing.price * order.quantity for order in orders if order.status == 'COMPLETED')
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
        listing__seller=request.user, 
        status='COMPLETED'
    ).annotate(
        date=TruncDate('date_ordered')
    ).values('date').annotate(
        total_sales=Sum(F('listing__price') * F('quantity'), output_field=DecimalField())
    ).order_by('date')
    
    # 2. Top Products by Quantity Sold
    top_products = Order.objects.filter(
        listing__seller=request.user,
        status='COMPLETED'
    ).values('listing__title').annotate(
        quantity_sold=Sum('quantity')
    ).order_by('-quantity_sold')[:5]
    
    # 3. Order Status Distribution
    status_dist = Order.objects.filter(
        listing__seller=request.user
    ).values('status').annotate(
        count=Count('status')
    )
    
    context = {
        'daily_sales': json.dumps(list(daily_sales), cls=DjangoJSONEncoder),
        'top_products': json.dumps(list(top_products), cls=DjangoJSONEncoder),
        'status_dist': json.dumps(list(status_dist), cls=DjangoJSONEncoder),
    }
    return render(request, 'analytics.html', context)
#   O r d e r   T r a c k i n g   V i e w s  
  
 f r o m   d j a n g o . u t i l s   i m p o r t   t i m e z o n e  
 f r o m   . m o d e l s   i m p o r t   O r d e r S t a t u s H i s t o r y  
  
 @ l o g i n _ r e q u i r e d  
 d e f   b u y e r _ o r d e r s ( r e q u e s t ) :  
         " " " D i s p l a y   a l l   o r d e r s   f o r   t h e   l o g g e d - i n   b u y e r " " "  
         o r d e r s   =   O r d e r . o b j e c t s . f i l t e r ( b u y e r = r e q u e s t . u s e r ) . o r d e r _ b y ( ' - d a t e _ o r d e r e d ' )  
          
         #   F i l t e r   b y   s t a t u s   i f   p r o v i d e d  
         s t a t u s _ f i l t e r   =   r e q u e s t . G E T . g e t ( ' s t a t u s ' )  
         i f   s t a t u s _ f i l t e r :  
                 o r d e r s   =   o r d e r s . f i l t e r ( s t a t u s = s t a t u s _ f i l t e r )  
          
         c o n t e x t   =   {  
                 ' o r d e r s ' :   o r d e r s ,  
                 ' s t a t u s _ f i l t e r ' :   s t a t u s _ f i l t e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' b u y e r _ o r d e r s . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   o r d e r _ d e t a i l ( r e q u e s t ,   o r d e r _ i d ) :  
         " " " D i s p l a y   d e t a i l e d   v i e w   o f   a   s p e c i f i c   o r d e r " " "  
         o r d e r   =   g e t _ o b j e c t _ o r _ 4 0 4 ( O r d e r ,   i d = o r d e r _ i d )  
          
         #   E n s u r e   u s e r   h a s   p e r m i s s i o n   t o   v i e w   t h i s   o r d e r  
         i f   o r d e r . b u y e r   ! =   r e q u e s t . u s e r   a n d   o r d e r . l i s t i n g . s e l l e r   ! =   r e q u e s t . u s e r :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " Y o u   d o n ' t   h a v e   p e r m i s s i o n   t o   v i e w   t h i s   o r d e r . " )  
                 r e t u r n   r e d i r e c t ( ' h o m e ' )  
          
         #   G e t   s t a t u s   h i s t o r y  
         s t a t u s _ h i s t o r y   =   o r d e r . s t a t u s _ h i s t o r y . a l l ( )  
          
         c o n t e x t   =   {  
                 ' o r d e r ' :   o r d e r ,  
                 ' s t a t u s _ h i s t o r y ' :   s t a t u s _ h i s t o r y ,  
                 ' i s _ f a r m e r ' :   o r d e r . l i s t i n g . s e l l e r   = =   r e q u e s t . u s e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' o r d e r _ d e t a i l . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   f a r m e r _ o r d e r s ( r e q u e s t ) :  
         " " " D i s p l a y   a l l   o r d e r s   f o r   t h e   l o g g e d - i n   f a r m e r ' s   l i s t i n g s " " "  
         #   G e t   a l l   o r d e r s   f o r   t h i s   f a r m e r ' s   l i s t i n g s  
         f a r m e r _ l i s t i n g s   =   L i s t i n g . o b j e c t s . f i l t e r ( s e l l e r = r e q u e s t . u s e r )  
         o r d e r s   =   O r d e r . o b j e c t s . f i l t e r ( l i s t i n g _ _ i n = f a r m e r _ l i s t i n g s ) . o r d e r _ b y ( ' - d a t e _ o r d e r e d ' )  
          
         #   F i l t e r   b y   s t a t u s   i f   p r o v i d e d  
         s t a t u s _ f i l t e r   =   r e q u e s t . G E T . g e t ( ' s t a t u s ' )  
         i f   s t a t u s _ f i l t e r :  
                 o r d e r s   =   o r d e r s . f i l t e r ( s t a t u s = s t a t u s _ f i l t e r )  
          
         c o n t e x t   =   {  
                 ' o r d e r s ' :   o r d e r s ,  
                 ' s t a t u s _ f i l t e r ' :   s t a t u s _ f i l t e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' f a r m e r _ o r d e r s . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   u p d a t e _ o r d e r _ s t a t u s ( r e q u e s t ,   o r d e r _ i d ) :  
         " " " U p d a t e   t h e   s t a t u s   o f   a n   o r d e r   ( f a r m e r   o n l y ) " " "  
         o r d e r   =   g e t _ o b j e c t _ o r _ 4 0 4 ( O r d e r ,   i d = o r d e r _ i d )  
          
         #   E n s u r e   o n l y   t h e   f a r m e r   c a n   u p d a t e  
         i f   o r d e r . l i s t i n g . s e l l e r   ! =   r e q u e s t . u s e r :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " Y o u   d o n ' t   h a v e   p e r m i s s i o n   t o   u p d a t e   t h i s   o r d e r . " )  
                 r e t u r n   r e d i r e c t ( ' h o m e ' )  
          
         i f   r e q u e s t . m e t h o d   = =   ' P O S T ' :  
                 f o r m   =   O r d e r S t a t u s U p d a t e F o r m ( r e q u e s t . P O S T ,   i n s t a n c e = o r d e r )  
                 i f   f o r m . i s _ v a l i d ( ) :  
                         o l d _ s t a t u s   =   o r d e r . s t a t u s  
                         o r d e r   =   f o r m . s a v e ( c o m m i t = F a l s e )  
                          
                         #   U p d a t e   t i m e s t a m p s   b a s e d   o n   n e w   s t a t u s  
                         i f   o r d e r . s t a t u s   = =   ' C O N F I R M E D '   a n d   n o t   o r d e r . c o n f i r m e d _ a t :  
                                 o r d e r . c o n f i r m e d _ a t   =   t i m e z o n e . n o w ( )  
                         e l i f   o r d e r . s t a t u s   = =   ' S H I P P E D '   a n d   n o t   o r d e r . s h i p p e d _ a t :  
                                 o r d e r . s h i p p e d _ a t   =   t i m e z o n e . n o w ( )  
                         e l i f   o r d e r . s t a t u s   = =   ' D E L I V E R E D '   a n d   n o t   o r d e r . d e l i v e r e d _ a t :  
                                 o r d e r . d e l i v e r e d _ a t   =   t i m e z o n e . n o w ( )  
                          
                         o r d e r . s a v e ( )  
                          
                         #   C r e a t e   s t a t u s   h i s t o r y   e n t r y  
                         O r d e r S t a t u s H i s t o r y . o b j e c t s . c r e a t e (  
                                 o r d e r = o r d e r ,  
                                 s t a t u s = o r d e r . s t a t u s ,  
                                 c h a n g e d _ b y = r e q u e s t . u s e r ,  
                                 n o t e s = f o r m . c l e a n e d _ d a t a . g e t ( ' t r a c k i n g _ n o t e s ' ,   ' ' )  
                         )  
                          
                         m e s s a g e s . s u c c e s s ( r e q u e s t ,   f ' O r d e r   s t a t u s   u p d a t e d   t o   { o r d e r . g e t _ s t a t u s _ d i s p l a y ( ) } ' )  
                         r e t u r n   r e d i r e c t ( ' o r d e r _ d e t a i l ' ,   o r d e r _ i d = o r d e r . i d )  
         e l s e :  
                 f o r m   =   O r d e r S t a t u s U p d a t e F o r m ( i n s t a n c e = o r d e r )  
          
         c o n t e x t   =   {  
                 ' f o r m ' :   f o r m ,  
                 ' o r d e r ' :   o r d e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' u p d a t e _ o r d e r _ s t a t u s . h t m l ' ,   c o n t e x t )  
 #   O r d e r   T r a c k i n g   V i e w s  
 #   O r d e r   T r a c k i n g   V i e w s  
  
 f r o m   d j a n g o . u t i l s   i m p o r t   t i m e z o n e  
 f r o m   . m o d e l s   i m p o r t   O r d e r S t a t u s H i s t o r y  
  
 @ l o g i n _ r e q u i r e d  
 d e f   b u y e r _ o r d e r s ( r e q u e s t ) :  
         " " " D i s p l a y   a l l   o r d e r s   f o r   t h e   l o g g e d - i n   b u y e r " " "  
         o r d e r s   =   O r d e r . o b j e c t s . f i l t e r ( b u y e r = r e q u e s t . u s e r ) . o r d e r _ b y ( ' - d a t e _ o r d e r e d ' )  
          
         #   F i l t e r   b y   s t a t u s   i f   p r o v i d e d  
         s t a t u s _ f i l t e r   =   r e q u e s t . G E T . g e t ( ' s t a t u s ' )  
         i f   s t a t u s _ f i l t e r :  
                 o r d e r s   =   o r d e r s . f i l t e r ( s t a t u s = s t a t u s _ f i l t e r )  
          
         c o n t e x t   =   {  
                 ' o r d e r s ' :   o r d e r s ,  
                 ' s t a t u s _ f i l t e r ' :   s t a t u s _ f i l t e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' b u y e r _ o r d e r s . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   o r d e r _ d e t a i l ( r e q u e s t ,   o r d e r _ i d ) :  
         " " " D i s p l a y   d e t a i l e d   v i e w   o f   a   s p e c i f i c   o r d e r " " "  
         o r d e r   =   g e t _ o b j e c t _ o r _ 4 0 4 ( O r d e r ,   i d = o r d e r _ i d )  
          
         #   E n s u r e   u s e r   h a s   p e r m i s s i o n   t o   v i e w   t h i s   o r d e r  
         i f   o r d e r . b u y e r   ! =   r e q u e s t . u s e r   a n d   o r d e r . l i s t i n g . s e l l e r   ! =   r e q u e s t . u s e r :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " Y o u   d o n ' t   h a v e   p e r m i s s i o n   t o   v i e w   t h i s   o r d e r . " )  
                 r e t u r n   r e d i r e c t ( ' h o m e ' )  
          
         #   G e t   s t a t u s   h i s t o r y  
         s t a t u s _ h i s t o r y   =   o r d e r . s t a t u s _ h i s t o r y . a l l ( )  
          
         c o n t e x t   =   {  
                 ' o r d e r ' :   o r d e r ,  
                 ' s t a t u s _ h i s t o r y ' :   s t a t u s _ h i s t o r y ,  
                 ' i s _ f a r m e r ' :   o r d e r . l i s t i n g . s e l l e r   = =   r e q u e s t . u s e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' o r d e r _ d e t a i l . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   f a r m e r _ o r d e r s ( r e q u e s t ) :  
         " " " D i s p l a y   a l l   o r d e r s   f o r   t h e   l o g g e d - i n   f a r m e r ' s   l i s t i n g s " " "  
         #   G e t   a l l   o r d e r s   f o r   t h i s   f a r m e r ' s   l i s t i n g s  
         f a r m e r _ l i s t i n g s   =   L i s t i n g . o b j e c t s . f i l t e r ( s e l l e r = r e q u e s t . u s e r )  
         o r d e r s   =   O r d e r . o b j e c t s . f i l t e r ( l i s t i n g _ _ i n = f a r m e r _ l i s t i n g s ) . o r d e r _ b y ( ' - d a t e _ o r d e r e d ' )  
          
         #   F i l t e r   b y   s t a t u s   i f   p r o v i d e d  
         s t a t u s _ f i l t e r   =   r e q u e s t . G E T . g e t ( ' s t a t u s ' )  
         i f   s t a t u s _ f i l t e r :  
                 o r d e r s   =   o r d e r s . f i l t e r ( s t a t u s = s t a t u s _ f i l t e r )  
          
         c o n t e x t   =   {  
                 ' o r d e r s ' :   o r d e r s ,  
                 ' s t a t u s _ f i l t e r ' :   s t a t u s _ f i l t e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' f a r m e r _ o r d e r s . h t m l ' ,   c o n t e x t )  
  
 @ l o g i n _ r e q u i r e d  
 d e f   u p d a t e _ o r d e r _ s t a t u s ( r e q u e s t ,   o r d e r _ i d ) :  
         " " " U p d a t e   t h e   s t a t u s   o f   a n   o r d e r   ( f a r m e r   o n l y ) " " "  
         o r d e r   =   g e t _ o b j e c t _ o r _ 4 0 4 ( O r d e r ,   i d = o r d e r _ i d )  
          
         #   E n s u r e   o n l y   t h e   f a r m e r   c a n   u p d a t e  
         i f   o r d e r . l i s t i n g . s e l l e r   ! =   r e q u e s t . u s e r :  
                 m e s s a g e s . e r r o r ( r e q u e s t ,   " Y o u   d o n ' t   h a v e   p e r m i s s i o n   t o   u p d a t e   t h i s   o r d e r . " )  
                 r e t u r n   r e d i r e c t ( ' h o m e ' )  
          
         i f   r e q u e s t . m e t h o d   = =   ' P O S T ' :  
                 f o r m   =   O r d e r S t a t u s U p d a t e F o r m ( r e q u e s t . P O S T ,   i n s t a n c e = o r d e r )  
                 i f   f o r m . i s _ v a l i d ( ) :  
                         o l d _ s t a t u s   =   o r d e r . s t a t u s  
                         o r d e r   =   f o r m . s a v e ( c o m m i t = F a l s e )  
                          
                         #   U p d a t e   t i m e s t a m p s   b a s e d   o n   n e w   s t a t u s  
                         i f   o r d e r . s t a t u s   = =   ' C O N F I R M E D '   a n d   n o t   o r d e r . c o n f i r m e d _ a t :  
                                 o r d e r . c o n f i r m e d _ a t   =   t i m e z o n e . n o w ( )  
                         e l i f   o r d e r . s t a t u s   = =   ' S H I P P E D '   a n d   n o t   o r d e r . s h i p p e d _ a t :  
                                 o r d e r . s h i p p e d _ a t   =   t i m e z o n e . n o w ( )  
                         e l i f   o r d e r . s t a t u s   = =   ' D E L I V E R E D '   a n d   n o t   o r d e r . d e l i v e r e d _ a t :  
                                 o r d e r . d e l i v e r e d _ a t   =   t i m e z o n e . n o w ( )  
                          
                         o r d e r . s a v e ( )  
                          
                         #   C r e a t e   s t a t u s   h i s t o r y   e n t r y  
                         O r d e r S t a t u s H i s t o r y . o b j e c t s . c r e a t e (  
                                 o r d e r = o r d e r ,  
                                 s t a t u s = o r d e r . s t a t u s ,  
                                 c h a n g e d _ b y = r e q u e s t . u s e r ,  
                                 n o t e s = f o r m . c l e a n e d _ d a t a . g e t ( ' t r a c k i n g _ n o t e s ' ,   ' ' )  
                         )  
                          
                         m e s s a g e s . s u c c e s s ( r e q u e s t ,   f ' O r d e r   s t a t u s   u p d a t e d   t o   { o r d e r . g e t _ s t a t u s _ d i s p l a y ( ) } ' )  
                         r e t u r n   r e d i r e c t ( ' o r d e r _ d e t a i l ' ,   o r d e r _ i d = o r d e r . i d )  
         e l s e :  
                 f o r m   =   O r d e r S t a t u s U p d a t e F o r m ( i n s t a n c e = o r d e r )  
          
         c o n t e x t   =   {  
                 ' f o r m ' :   f o r m ,  
                 ' o r d e r ' :   o r d e r ,  
         }  
         r e t u r n   r e n d e r ( r e q u e s t ,   ' u p d a t e _ o r d e r _ s t a t u s . h t m l ' ,   c o n t e x t )  
 