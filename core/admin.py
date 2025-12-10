from django.contrib import admin
from .models import Category, Profile, Listing, Order

admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Listing)
admin.site.register(Order)