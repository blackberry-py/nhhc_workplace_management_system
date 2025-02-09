"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
from typing import Callable

import allauth.urls
import defender.urls
import django_prometheus.urls
import health_check.urls
import robots.urls
import tinymce.urls

# from web.sitemaps import StaticViewSitemap.
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

import applications.announcements.urls
import applications.compliance.urls
import applications.employee.urls
import applications.portal.urls
import applications.web.urls
from common.errors import (
    bad_request_handler,
    maintenance_handler,
    page_not_found_handler,
    permission_denied_handler,
    server_error_handler,
)

# sitemaps= {"static": StaticViewSitemap}
# SECTION - Site-wide Error Handlers

handler400: Callable = bad_request_handler
handler403: Callable = permission_denied_handler
handler404: Callable = page_not_found_handler
handler500: Callable = server_error_handler
handler503: Callable = maintenance_handler
# SECTION - Master URL Route Patterns

urlpatterns = [
    path("control-center/defender/", include(defender.urls)),  # defender admin
    path("control-center/", admin.site.urls, name="admin"),
    # re_path(r"^sitemap.xml$\/?", cache_page(60)(sitemaps), {"sitemaps": sitemaps}, name="cached-sitemap"),
    re_path(r"^robots\.txt\/?", include(robots.urls)),
    re_path("", include(django_prometheus.urls), name="metric_scrape"),
    path(f"status/{os.environ['STATUS_URL_KEY']}/", include(health_check.urls)),
    path("maintenance/", maintenance_handler, name="maintenance_mode"),
    path("tinymce/", include(tinymce.urls)),
    path("", include(applications.portal.urls, namespace="portal")),
    path("", include(applications.web.urls, namespace="web")),
    path("", include(allauth.urls)),
    path("", include(applications.employee.urls, namespace="employee")),
    path("", include(applications.announcements.urls, namespace="announcements")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, re_path(r"^__debug__/", include(debug_toolbar.urls)))
