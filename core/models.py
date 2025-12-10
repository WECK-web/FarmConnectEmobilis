from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = "Categories"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=(('FARMER', 'Farmer'),('CONSUMER', 'Consumer')), default='CONSUMER')
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', default='default.jpg', blank=True)
    def __str__(self): return f"{self.user.username} ({self.user_type})"

class Listing(models.Model):
    seller = models.ForeignKey(User, related_name='listings', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='listings/', blank=True)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, choices=(('KG', 'Kg'),('SACK', 'Sack'),('BOX', 'Box')), default='KG')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Order(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('PENDING', 'Pending'),('COMPLETED', 'Collected')), default='PENDING')

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"From {self.sender} to {self.recipient}"