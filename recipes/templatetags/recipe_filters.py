from django import template

register = template.Library()


@register.filter
def get_range(value):
    """
    Returns a range of numbers from 1 to value
    Usage: {% for i in total_pages|add:'1'|get_range %}
    """
    try:
        value = int(value)
        return range(1, value)
    except (ValueError, TypeError):
        return range(0)


@register.filter
def split(value, arg):
    """Split a string by argument and return the list"""
    if value is None:
        return []
    return value.split(arg)


@register.filter
def get_range(value):
    """Return a range of numbers from 1 to value"""
    return range(1, int(value))
