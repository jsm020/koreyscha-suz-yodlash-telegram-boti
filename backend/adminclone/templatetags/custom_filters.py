from django import template

register = template.Library()

@register.filter
def attr(obj, field_name):
    try:
        return getattr(obj, field_name)
    except AttributeError:
        return ''