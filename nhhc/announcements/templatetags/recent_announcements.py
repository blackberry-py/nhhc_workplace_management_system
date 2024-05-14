from announcements.models import Announcements
from django import template

register = template.Library()


@register.inclusion_tag("_announcements.html")
def recent_announcements():
    announcements = Announcements.objects.queryset_from_cache().filter(status="A").order_by("-date_posted")[:5]
    return {"recent_announcements": announcements}
