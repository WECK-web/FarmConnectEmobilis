from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Profile, Listing, Order, Message
from decimal import Decimal

class FarmConnectTests(TestCase):
    def setUp(self):
        # Create Users
        self.farmer_user = User.objects.create_user(username='farmer', password='password')
        Profile.objects.create(user=self.farmer_user, user_type='FARMER', location='Farmville')
        
        self.consumer_user = User.objects.create_user(username='consumer', password='password')
        Profile.objects.create(user=self.consumer_user, user_type='CONSUMER', location='City')
        
        # Create Category
        self.category = Category.objects.create(name='Vegetables')
        
        # Create Listing
        self.listing = Listing.objects.create(
            seller=self.farmer_user,
            category=self.category,
            title='Fresh Carrots',
            description='Crunchy carrots',
            quantity=10,
            unit='KG',
            price=Decimal('5.00'),
            expiry_date='2025-12-31'
        )
        
        self.client = Client()

    def test_cart_add_and_checkout(self):
        # Login as consumer
        self.client.login(username='consumer', password='password')
        
        # Add to cart
        response = self.client.post(reverse('cart_add', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302) # Redirects to cart_detail
        
        # Check cart in session
        session = self.client.session
        self.assertIn('cart', session)
        self.assertIn(str(self.listing.id), session['cart'])
        
        # Checkout
        response = self.client.post(reverse('checkout'))
        self.assertEqual(response.status_code, 200) # Renders success page
        
        # Verify Order created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.buyer, self.consumer_user)
        self.assertEqual(order.listing, self.listing)
        self.assertEqual(order.status, 'PENDING')

    def test_search_functionality(self):
        response = self.client.get(reverse('home'), {'q': 'Carrots'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Carrots')
        
        response = self.client.get(reverse('home'), {'q': 'Potatoes'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Fresh Carrots')

    def test_farmer_dashboard_stats(self):
        # Create a completed order
        Order.objects.create(listing=self.listing, buyer=self.consumer_user, status='COMPLETED')
        
        self.client.login(username='farmer', password='password')
        response = self.client.get(reverse('farmer_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check stats in context
        self.assertEqual(response.context['listings'].count(), 1)
        self.assertEqual(response.context['total_sales'], Decimal('5.00'))

    def test_messaging(self):
        self.client.login(username='consumer', password='password')
        
        # Send message
        response = self.client.post(reverse('send_message', args=['farmer']), {'body': 'Is this organic?'})
        self.assertEqual(response.status_code, 302) # Redirects to inbox
        
        # Verify message created
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(msg.sender, self.consumer_user)
        self.assertEqual(msg.recipient, self.farmer_user)
        self.assertEqual(msg.body, 'Is this organic?')

    def test_order_status_update(self):
        order = Order.objects.create(listing=self.listing, buyer=self.consumer_user, status='PENDING')
        
        self.client.login(username='farmer', password='password')
        response = self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'COMPLETED'})
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'COMPLETED')
