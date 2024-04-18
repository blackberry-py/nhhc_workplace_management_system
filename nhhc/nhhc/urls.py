"""nhhc URL Configuration

The `urlpatterns` list routes URLs to views.
"""
import announcements.urls
import authentication.urls
import compliance.urls
import employee.urls
import portal.urls
import web.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from loguru import logger
from web.sitemaps import StaticViewSitemap
from django.conf import settings

sitemaps = {"static": StaticViewSitemap}
from django.http import HttpResponse
from django.http import HttpRequest

urlpatterns = [
    path("control-center/", admin.site.urls),
    re_path(r"^compliance/", include("filer.urls")),
    re_path(r"^", include("filer.server.urls")),
    path("", include(web.urls)),
    path("", include("allauth.urls")),
    re_path(
        r"^status/DNzaNdlwIbqjWCq4vMTAgGe81VxXFd1QPGt-mglUDuA/",
        include("health_check.urls"),
    ),
    # path("", include(authentication.urls)),
    path("", include(portal.urls)),
    path("", include(employee.urls)),
    path("", include(compliance.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("", include(announcements.urls)),
    re_path(
        r"^sitemap.xml$",
        cache_page(60)(sitemaps),
        {"sitemaps": sitemaps},
        name="cached-sitemap",
    ),
    re_path(r"^robots\.txt", include("robots.urls")),
    re_path("", include("django_prometheus.urls")),
]
# if settings.DEBUG is False:
#      urlpatterns  = urlpatterns + [ path("__debug__/", include("debug_toolbar.urls")),
# ]
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}


def bad_request_handler(request: HttpRequest, exception=None):
    logger.warning(f"BAD REQUEST: {exception}")
    return render(request, "400.html", status=400)


def permission_denied_handler(request: HttpRequest, exception=None):
    logger.error(f"FORBIDDEN ERROR: {exception}")
    return render(request, "403_csrf.html", status=403)


def page_not_found_handler(request: HttpRequest, exception=None):
    logger.warning(f"PAGE NOT FOUND ERROR: {exception}")
    return render(request, "404.html", status=404)


def server_error_handler(request: HttpRequest, exception=None):
    logger.error(f"SERVER ERROR: {exception}")
    return render(request, "500.html", status=500)


handler400 = bad_request_handler
handler403 = permission_denied_handler
handler404 = page_not_found_handler
handler500 = server_error_handler
