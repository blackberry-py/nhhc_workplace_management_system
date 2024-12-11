"""nhhc URL Configuration

The `urlpatterns` list routes URLs to views.
"""
import json
from typing import Callable, Dict, List, Union

import announcements.urls
import compliance.urls
import employee.urls
import portal.urls
import web.urls
import defender.urls
import robots.urls
import django_prometheus.urls
import tinymce.urls
import health_check.urls

# import maintenance_mode.urls
import rest_framework.urls
import allauth.urls
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps import Sitemap
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import include, path, re_path
from django.urls.resolvers import RegexPattern, RoutePattern
from django.views.decorators.cache import cache_page
from loguru import logger
from web.sitemaps import StaticViewSitemap
from django.conf import settings
from django_require_login.mixins import public

# SECTION - Sitemap
sitemaps: Dict[str, Sitemap] = {"static": StaticViewSitemap}
#!SECTION

# SECTION - Health Check

HEALTH_CHECK: Dict[str, int] = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}

#!SECTION


# SECTION - Sitewide Error Handlers
@public
def maintenance_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle bad requests by logging the exception and rendering a 400.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """

    return render(request, "503.html", status=503)


def bad_request_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle bad requests by logging the exception and rendering a 400.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """

    logger.warning(f"BAD REQUEST: {exception}")
    return render(request, "400.html", status=400)


def permission_denied_handler(request: HttpRequest, reason=None) -> HttpResponse:
    """
    Handle forbidden requests by logging the exception and rendering a 403.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """
    logger.error(f"FORBIDDEN ERROR: {reason}")
    return render(request, "403_csrf.html", status=403)


def page_not_found_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle requests where the route is not found by logging the exception and rendering a 404.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 404 and the 404.html template rendered.
    """
    logger.warning(f"PAGE NOT FOUND ERROR: {exception}")
    return render(request, "404.html", status=404)


def server_error_handler(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Handle requests that result in server errors by logging the exception and rendering a 500.html template.

    Args:
        request (HttpRequest): The HTTP request object.
        exception (Exception, optional): The exception that caused the bad request. Defaults to None.

    Returns:
        HttpResponse: A response with status code 400 and the 400.html template rendered.
    """
    logger.error(f"SERVER ERROR: {exception}")
    return render(request, "500.html", status=500)


handler400: Callable = bad_request_handler
handler403: Callable = permission_denied_handler
handler404: Callable = page_not_found_handler
handler500: Callable = server_error_handler
handler503: Callable = maintenance_handler
#!SECTION


# SECTION - Master URL Route Patterns

urlpatterns: List[Union[RoutePattern, RegexPattern]] = [
    path("control-center/defender/", include(defender.urls)),  # defender admin
    path("control-center/", admin.site.urls, name="admin"),
    re_path(r"^sitemap.xml$\/?", cache_page(60)(sitemaps), {"sitemaps": sitemaps}, name="cached-sitemap"),
    re_path(r"^robots\.txt\/?", include(robots.urls)),
    re_path("", include(django_prometheus.urls), name="metric_scrape"),
    re_path(r"^status/", include(health_check.urls)),
    path("maintenance/", maintenance_handler, name="maintenance_mode"),
    path("tinymce/", include(tinymce.urls)),
    path("", include(portal.urls)),
    path("", include(web.urls)),
    path("", include(allauth.urls)),
    path("", include(employee.urls)),
    path("", include(announcements.urls)),
]
#!SECTION
if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, re_path(r"^__debug__/", include(debug_toolbar.urls)))
