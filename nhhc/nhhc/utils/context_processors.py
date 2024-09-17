from django.conf import settings
from django.template import RequestContext
from portal.forms import PayrollExceptionForm
from django.http import HttpRequest
from typing import Dict, Any
import re


def global_forms(request: HttpRequest) -> Dict[str, Any]:
    pattern = re.compile(r"[a-z0-9]+://[a-z0-9]+:\d.*/login/", re.IGNORECASE)
    if request.method == "POST" and request.user.is_authenticated:
        form = PayrollExceptionForm(request.POST)
    else:
        form = PayrollExceptionForm()
    return {"ExceptionForm": form}


def from_settings(request):
    return {
        "ENVIRONMENT_NAME": settings.ENVIRONMENT_NAME,
        "ENVIRONMENT_COLOR": settings.ENVIRONMENT_COLOR,
    }

def maintenance_mode(request):
    if settings.MAINTENANCE_MODE:
        return {"MAINTENANCE_MODE": True}
