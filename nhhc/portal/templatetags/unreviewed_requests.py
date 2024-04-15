from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db.models.query import QuerySet
from django.utils.html import format_html
from typing import Union, Optional, Dict
from web.models import EmploymentApplicationModel, ClientInterestSubmissions
from django.utils.safestring import SafeText

register = template.Library()


@register.inclusion_tag(name="app_count", filename="_unreviewed_employment_applications.html")
def render_unreviewed_employment_apps() -> Dict[str, int]:
    employment_apps = EmploymentApplicationModel.objects.filter(reviewed__in=[False, None]).count()
    return {"app_count": int(employment_apps)}


@register.inclusion_tag(name="client_count", filename="_unreviewed_client_requests.html")
def render_unreviewed_employment_apps() -> Dict[str, int]:
    client_requests = ClientInterestSubmissions.objects.filter(reviewed__in=[False, None]).count()
    return {"client_count": int(client_requests)}
