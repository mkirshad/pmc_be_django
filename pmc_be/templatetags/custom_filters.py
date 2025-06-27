# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def format_currency(value):
    try:
        return f"PKR {value:,.2f}"
    except (ValueError, TypeError):
        return value
