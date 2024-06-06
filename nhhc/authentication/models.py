from collections.abc import Callable
from uuid import uuid4

from compliance.models import Compliance
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django_extensions.db.models import TimeStampedModel
from employee.models import Employee
from loguru import logger


class UserProfile(TimeStampedModel, models.Model):
    user = models.OneToOneField(Employee, unique=True, on_delete=models.CASCADE)
    force_password_change = models.BooleanField(default=True)
    last_password_change = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"User Profile of {self.user.last_name}, {self.user.first_name} ({self.user.employee_id})"

    def queryset_from_cache(self, filterdict):
        cachekey = "userprofile"
        qs = cache.get(cachekey)

        if qs:
            d = {"in_cache": True, "qs": qs}
        else:
            qs = UserProfile.objects.filter(**filterdict)
            cache.set(cachekey, qs, 300)  # 5 min cache
            d = {"in_cache": False, "qs": qs}
        return d
