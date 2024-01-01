from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value):
    """
    Replace occurrences of arg[0] with arg[1] in the given value.
    Usage: {{ some_text|replace}}
    """
    return value.replace("/", "%252F")
