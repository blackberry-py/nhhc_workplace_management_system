from django import template

register = template.Library()


@register.filter
def human_readable(value):
    return f"get_{value}_display"
