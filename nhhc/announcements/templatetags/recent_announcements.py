from announcements.models import Announcements
from django import template

register = template.Library()


@register.inclusion_tag("_announcements.html")
def recent_announcements():
    context = dict()
    announcements = Announcements.objects.filter(status="A").order_by("-date_posted")[
        :5
    ]
    context["announcements"] = announcements
    return context
