from decimal import Decimal
from django.conf import settings
from .models import Listing

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, listing, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        listing_id = str(listing.id)
        if listing_id not in self.cart:
            self.cart[listing_id] = {'quantity': 0, 'price': str(listing.price)}
        
        if update_quantity:
            self.cart[listing_id]['quantity'] = quantity
        else:
            self.cart[listing_id]['quantity'] += quantity
        self.save()

    def remove(self, listing):
        """
        Remove a product from the cart.
        """
        listing_id = str(listing.id)
        if listing_id in self.cart:
            del self.cart[listing_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        listing_ids = self.cart.keys()
        listings = Listing.objects.filter(id__in=listing_ids)
        cart = self.cart.copy()

        for listing in listings:
            cart[str(listing.id)]['listing'] = listing

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True
