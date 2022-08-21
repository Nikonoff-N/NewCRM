from django import template

register = template.Library()

@register.simple_tag
def get_username(request):
    if request.user.is_authenticated:
        user = request.user.username
        return user
    else:
        return False