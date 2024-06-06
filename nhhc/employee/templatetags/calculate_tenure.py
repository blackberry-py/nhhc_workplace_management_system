from datetime import datetime

import arrow
from django import template

register = template.Library()


@register.inclusion_tag("includes/_tenure.html", takes_context=True)
def tenure(context):
    print(context)
    start_date = arrow.get(context["hire_date"])
    current_date = arrow.now()
    tenure = start_date.humanize(current_date, granularity=["year", "month", "day"])
    return tenure


@register.inclusion_tag("includes/_total_tenure.html", takes_context=True)
def total_tenure(context):
    start_date = arrow.get(context["hire_date"])
    end_date = arrow.get(context["termination_date"])
    # tenure = current_date - start_date
    total_tenure = start_date.humanize(end_date, granularity=["year", "month", "day"])
    return total_tenure


# @register.filter()
# def tenure(value):
#     start_date = arrow.get(value)
#     current_date = arrow.now()
#     tenure = start_date.humanize(current_date,granularity=["year", "month", "day"] )
#     return tenure


# @register.filter()
# def total_tenure(start, end):
#     start_date = arrow.get(start )
#     end_date = arrow.get(end)
#     # tenure = current_date - start_date
#     total_tenure = start_date.humanize(end_date ,granularity=["year", "month", "day"] )
#     return total_tenure
