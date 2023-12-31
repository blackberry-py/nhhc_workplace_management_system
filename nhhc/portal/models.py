"""
Module: portal.models

This module contains the models for handling payroll exceptions in the system. It includes the Exception model, which represents a payroll exception entry, and defines the fields and their validation rules.

The Exception model includes the following fields:
- date: Date of the exception
- start_time: Start time of the exception
- end_time: End time of the exception
- num_hours: Number of hours for the exception
- reason: Reason for the exception, with a minimum length validation of 50 characters
- status: Status of the exception, with predefined choices of Pending, Approved, and Rejected

The module also includes the Meta class for defining database table name, ordering, and verbose names.

Note: The Assessment and InServiceTraining models are currently commented out and not in use.

"""

import arrow
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prometheus.models import ExportModelOperationsMixin

now = arrow.now(tz="America/Chicago")


class Exception(models.Model, ExportModelOperationsMixin("exceptions")):
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
