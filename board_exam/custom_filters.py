# custom_filters.py

from django import template

register = template.Library()

@register.filter
def starts_with(value, arg):
    return value.startswith(arg)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

