from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

class BanEnforcementMiddleware:
    """
    Middleware to enforce bans on users who are already logged in.
    If a logged-in user becomes inactive (banned), they are logged out immediately.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            # Force logout
            logout(request)
            messages.error(request, "Your account has been suspended by the administrator.")
            return redirect('login')

        response = self.get_response(request)
        return response
