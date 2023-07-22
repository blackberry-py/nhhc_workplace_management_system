from django import template

register = template.Library()


@register.filter(name="anonymize")
def anonymize(value):
    if value is None:
        value = "Employee Has Not Entered"
    else:
        anonymized_prefix = "***-**-"
        value = anonymized_prefix + value[-4:]
    return value
