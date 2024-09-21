from django.shortcuts import redirect
from django.conf import settings
from django.urls import  reverse
import re

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        ignoreableurls = [reverse("maintenance_mode"),
                          reverse("prometheus-django-metrics"),
                          r"\/control-center\/([^\s]+)"
                          ]
        for url in ignoreableurls:
            if settings.MAINTENANCE_MODE and (not re.match(url, path) or path != url) :
                    return redirect(reverse("maintenance_mode"))
        # elif settings.MAINTENANCE_MODE and path != e:
        #     return redirect(reverse("maintenance_mode"))
        # elif settings.MAINTENANCE_MODE and path != reverse("admin"):
        #     return redirect(reverse("maintenance_mode"))
        # else:
            return self.get_response(request)