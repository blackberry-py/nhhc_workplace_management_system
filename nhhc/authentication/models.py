from collections.abc import Callable
from uuid import uuid4

from compliance.models import Compliance
from django.conf import settings
from django.db import models
from employee.models import Employee
from loguru import logger


class UserProfile(models.Model):
    user = models.OneToOneField(Employee, unique=True, on_delete=models.CASCADE)
    force_password_change = models.BooleanField(default=True)
    last_password_change = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"User Profile of {self.user.last_name}, {self.user.first_name} ({self.user.employee_id})"


def create_user_profile_signal(sender: Callable, instance, created, **kwargs) -> None:
    if created:
        UserProfile.objects.create(user=instance)
        logger.debug(f"Signal Triggered for UserProfile Creation for {instance}")
        Compliance.objects.create(employee=instance)
        logger.debug(f"Signal Triggered for Compliance Creation for {instance}")


def password_change_signal(sender, instance, **kwargs) -> None:
    try:
        user = Employee.objects.get(username=instance.username)
        if not user.password == instance.password:
            profile = user.get_profile()
            profile.force_password_change = False
            profile.save()
    except Employee.DoesNotExist:
        pass
