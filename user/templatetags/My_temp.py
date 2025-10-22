from django.template.library import Library
from user.models import CustomUser
from django.shortcuts import get_list_or_404


register = Library()



@register.filter
def my_lower(value):
    """Convert a string into all lowercase."""
    return value.lower()
@register.simple_tag()
def get_user():
    users = get_list_or_404(CustomUser)
    return users