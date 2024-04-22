"""
Module: nhhc.portal.templatetags.unreviewed_requests

This module contains custom template tags for rendering the count of unreviewed employment applications and unreviewed client requests.

Functions:
1. render_unreviewed_employment_apps()
    - Description: Renders the count of unreviewed employment applications.
    - Returns: A dictionary containing the count of unreviewed employment applications.

2. render_unreviewed_client_requests()
    - Description: Renders the number of unreviewed client requests.
    - Returns: A dictionary containing the count of unreviewed client requests.
"""
from typing import Dict

from django import template
from web.models import ClientInterestSubmissions, EmploymentApplicationModel

register = template.Library()


@register.inclusion_tag(name="app_count", filename="_unreviewed_employment_applications.html")
def render_unreviewed_employment_apps() -> Dict[str, int]:
    """
    This function is a custom template tag that renders the count of unreviewed employment applications.

    Returns:
    Dict[str, int]: A dictionary containing the count of unreviewed employment applications.
    """
    employment_apps = EmploymentApplicationModel.objects.filter(reviewed=False).count()
    return {"app_count": int(employment_apps)}


@register.inclusion_tag(name="client_count", filename="_unreviewed_client_requests.html")
def render_unreviewed_client_requests() -> Dict[str, int]:
    """
    This function renders the number of unreviewed client requests.

    Returns:
    Dict[str, int]: A dictionary containing the count of unreviewed client requests.
    """
    client_requests = ClientInterestSubmissions.objects.filter(reviewed__in=[False, None]).count()
    return {"client_count": int(client_requests)}
