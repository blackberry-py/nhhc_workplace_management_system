import re

from authentication.models import UserProfile
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.deprecation import MiddlewareMixin


class PasswordChangeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not re.match(r"/__debug__/", request.path) and not re.match(r"^/password/change/?", request.path):
            profile = UserProfile.objects.get(user=request.user)
            if profile.force_password_change:
                return HttpResponseRedirect(reverse("account_change_password"), {"first_time": True})
