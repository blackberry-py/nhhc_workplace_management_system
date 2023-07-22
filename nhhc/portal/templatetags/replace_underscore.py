from django import template

register = template.Library()


@register.filter(name="replace_underscores")
def replace_underscores(value):
    value = value.replace("_", " ")
    return value.title()
