"""nhhc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import announcements.urls
import authentication.urls
import compliance.urls
import employee.urls
import portal.urls
import web.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path, re_path
from django.contrib.sitemaps.views import sitemap
from web.sitemaps import StaticViewSitemap
from django.views.generic.base import TemplateView

from loguru import logger
sitemaps = {
    'static': StaticViewSitemap
}
from django.http import HttpResponse

urlpatterns = [
    path("control-center/", admin.site.urls),
    path("", include(web.urls)),
    path("", include(authentication.urls)),
    path("", include(portal.urls)),
    path("", include(employee.urls)),
    path("", include(compliance.urls)),
    path("", include(announcements.urls)),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt/', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # path("404/", web.views.handler404),
    # path("500/", web.views.handler500)
]

handler404 = web.views.handler404
handler500 = web.views.handler500
