from django import template

register = template.Library()


@register.filter(name="anonymize")
def anonymize(value):
    value = "Employee Has Not Entered" if value is None else f"***-**-{value[-4:]}"
    return value
