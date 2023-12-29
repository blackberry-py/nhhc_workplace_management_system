import arrow
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from employee.models import Employee
from localflavor.us.models import (
    USSocialSecurityNumberField,
    USStateField,
    USZipCodeField,
)
from phonenumber_field.modelfields import PhoneNumberField

now = arrow.now(tz="America/Chicago")


class Exception(models.Model):
    class STATUS(models.TextChoices):
        PENDING = "P", _("Pending - Awaiting Supervisor Review")
        APPROVED = "A", _("Approved - Time Amended")
        REJECTED = "R", _("Rejected")

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    num_hours = models.PositiveIntegerField()
    reason = models.TextField(
        validators=[
            MinLengthValidator(50, "the field must contain at least 50 characters"),
        ],
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS.choices,
        default=STATUS.PENDING,
    )

    class Meta:
        db_table = "payroll_exceptions"
        ordering = ["-date"]
        verbose_name = "Payroll Exception"
        verbose_name_plural = "Payroll Exceptions"


# class Assessment(models.Model):
#     user = models.ForeignKey("Employee", on_delete=models.CASCADE)
#     attempt_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return ""


# class InServiceTraining(models.Model):
#     user = models.ForeignKey("Employee", on_delete=models.CASCADE)

#     def __str__(self):
#         return ""
