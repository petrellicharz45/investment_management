from django import template

register = template.Library()

@register.filter
def capitalize_first(value):
    if value and isinstance(value, str):
        return value.capitalize()
    return value