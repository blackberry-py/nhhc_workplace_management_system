from announcements.models import Announcements
from django import template

register = template.Library()


@register.inclusion_tag("_announcements.html")
def recent_announcements():
    announcements = Announcements.objects.all().filter(status="A").order_by("-date_posted")[:5]
    logger.debug(announcements)
    return {"recent_announcements": announcements}
