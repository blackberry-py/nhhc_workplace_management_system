import re
from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest

from applications.portal.forms import PayrollExceptionForm


def global_forms(request: HttpRequest) -> Dict[str, Any]:
    pattern = re.compile(r"[a-z0-9]+://[a-z0-9]+:\d.*/login/", re.IGNORECASE)
    if request.method == "POST" and request.user.is_authenticated:
        form = PayrollExceptionForm(request.POST)
    else:
        form = PayrollExceptionForm()
    return {"ExceptionForm": form}


def maintenance_mode(request):
    if settings.MAINTENANCE_MODE:
        return {"MAINTENANCE_MODE": True}
