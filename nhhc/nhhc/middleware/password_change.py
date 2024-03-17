import re

from django.http import HttpResponseRedirect
from django.shortcuts import reverse


class PasswordChangeMiddleware:
    def process_request(self, request):
        if (
            request.user.is_authenticated()
            and re.match(r"^/admin/?", request.path)
            and not re.match(r"^/admin/password_change/?", request.path)
        ):
            profile = request.user.get_profile()
            if profile.force_password_change:
                return HttpResponseRedirect(reverse("account_change_password"))
