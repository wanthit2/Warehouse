# custom_filters.py
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    """ ใช้ดึงค่าจาก Dictionary ตาม key """
    return dictionary.get(key, None)