from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure user is authenticated first
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check profile
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            if not profile.phone or not profile.location:
                messages.warning(request, "Please complete your profile (add phone and location) to continue.")
                return redirect('profile')
        else:
            # Should exist due to signal/logic, but if not:
            return redirect('profile')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
