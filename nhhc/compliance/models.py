from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from employee.models import Employee
from django_backblaze_b2 import BackblazeB2Storage

storage_opts = {
    "bucket": "nhhc-employee",
}


class Contract(models.Model, ExportModelOperationsMixin("contracts")):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "contracts"
        ordering = ["code"]
        verbose_name = "State Contract"
        verbose_name_plural = "State Contracts"


class Compliance(models.Model, ExportModelOperationsMixin("compliance")):
    class JOB_TITLE(models.TextChoices):
        AIDE = "AIDE", _("Homecare Aide")
        COORDINATOR = "CARE_COORDINATOR", _("Care Coordinator")
        CC_SUPERVISOR = "CARE_COORDINATOR_SUPERVISOR", _("Care Coordinator Supervisor")
        HC_SUPERVISOR = "HOMECARE_SUPERVISOR", _("Homecare Supervisor")

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="compliance_profile_of",
    )
    aps_check_passed = models.BooleanField(null=True, blank=True)
    aps_check_verification = models.FileField(
        upload_to="nhhc-employee", null=True, blank=True, storage=BackblazeB2Storage
    )
    hhs_oig_exclusionary_check_verification = models.FileField(
        upload_to="nhhc-employee", null=True, blank=True, storage=BackblazeB2Storage
    )
    hhs_oig_exclusionary_check_completed = models.BooleanField(
        null=True,
        blank=True,
        default=False,
    )
    idph_background_check_completed = models.BooleanField(
        null=True,
        blank=True,
        default=False,
    )
    idph_background_check_verification = models.FileField(
        upload_to="nhhc-employee", null=True, blank=True, storage=BackblazeB2Storage
    )
    initial_idph_background_check_completion_date = models.DateField(
        null=True,
        blank=True,
    )
    current_idph_background_check_completion_date = models.DateField(
        null=True,
        blank=True,
    )
    training_exempt = models.BooleanField(null=True, blank=True, default=False)
    pre_training_verification = models.FileField(
        upload_to="nhhc-employee", null=True, blank=True, storage=BackblazeB2Storage
    )
    pre_service_completion_date = models.DateField(null=True, blank=True)
    added_to_TTP_portal = models.BooleanField(null=True, blank=True)
    contract_code = models.ForeignKey(
        Contract, on_delete=models.PROTECT, blank=True, null=True
    )
    job_title = models.CharField(
        null=True,
        choices=JOB_TITLE.choices,
        default=JOB_TITLE.AIDE,
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.job_title}"

    class Meta:
        db_table = "audit_compliance"
        ordering = ["employee"]
        verbose_name = "Compliance-Auditing Data"
        verbose_name_plural = "Compliance-Auditing Data"
