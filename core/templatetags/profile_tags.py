from django import template

register = template.Library()

@register.filter
def get_user_type(user):
    """Safely get user type, defaulting to CONSUMER if profile doesn't exist"""
    try:
        return user.profile.user_type
    except:
        return 'CONSUMER'

@register.filter
def has_profile(user):
    """Check if user has a profile"""
    return hasattr(user, 'profile')
