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
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_prometheus.models import ExportModelOperationsMixin
from employee.models import Employee

now = arrow.now(tz="America/Chicago")


class PayrollException(models.Model, ExportModelOperationsMixin("exceptions")):
    """
    A model to represent exceptions in the payroll system.

    Attributes:
    - date (DateField): The date of the exception.
    - start_time (TimeField): The start time of the exception.
    - end_time (TimeField): The end time of the exception.
    - num_hours (PositiveIntegerField): The number of hours for the exception.
    - reason (TextField): The reason for the exception, must be at least 50 characters long.
    - status (CharField): The status of the exception, with choices of 'P' for Pending, 'A' for Approved, and 'R' for Rejected.
    - date_submitted (CreationDateTimeField): The date and time the exception was submitted.
    - last_modified (ModificationDateTimeField): The date and time the exception was last modified.

    Meta:
    - db_table: "payroll_exceptions"
    - ordering: ["-date"]
    - verbose_name: "Payroll Exception"
    - verbose_name_plural: "Payroll Exceptions"
    """

    class STATUS(models.TextChoices):
        """
        Enum Values for Status Class
        """

        PENDING = "P", _("Pending - Awaiting Supervisor Review")
        APPROVED = "A", _("Approved - Time Amended")
        REJECTED = "R", _("Rejected")

    date = models.DateField()
    requesting_employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="requesting_employee", null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    reviewer = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="exception_reviewer")
    num_hours = models.PositiveIntegerField()
    rejection_reason = models.TextField(null=True, blank=True)
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
    date_submitted = CreationDateTimeField()
    last_modified = ModificationDateTimeField()

    class Meta:
        """
        This class defines metadata options for the Exception model.
        """

        db_table = "payroll_exceptions"
        ordering = ["-date"]
        verbose_name = "Payroll Exception"
        verbose_name_plural = "Payroll Exceptions"

    def approve_exception(self, reviewer: Employee) -> None:
        self.status = "A"
        self.reviewer = reviewer.employee_id

    def reject_exception(self, reviewer: Employee) -> None:
        self.status = "R"
        self.reviewer = reviewer.employee_id


# class Assessment(models.Model):
#     user = models.ForeignKey("Employee", on_delete=models.CASCADE)
#     attempt_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return ""


# class InServiceTraining(models.Model):
#     user = models.ForeignKey("Employee", on_delete=models.CASCADE)

#     def __str__(self):
#         return ""
