from django.contrib import admin
from .models import Category, Profile, Listing, Order, Review, Message, Notification, Payment, Wishlist

admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Listing)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(Wishlist)