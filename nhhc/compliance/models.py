from django.db import models
from django.utils.translation import gettext_lazy as _
from employee.models import Employee


class Contract(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "contracts"
        ordering = ["code"]
        verbose_name = "State Contract"
        verbose_name_plural = "State Contracts"


class Compliance(models.Model):
    class JOB_TITLE(models.TextChoices):
        AIDE = "AIDE", _("Homecare Aide")
        COORDINATOR = "CARE_COORDINATOR", _("Care Coordinator")
        CC_SUPERVISOR = "CARE_COORDINATOR_SUPERVISOR", _("Care Coordinator Supervisor")
        HC_SUPERVISOR = "HOMECARE_SUPERVISOR", _("Homecare Supervisor")

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    aps_check_passed = models.BooleanField(null=True, blank=True)
    aps_check_verification = models.FileField(
        upload_to="verifications",
        null=True,
        blank=True,
    )
    hhs_oig_exclusionary_check_verification = models.FileField(
        upload_to="verifications",
        null=True,
        blank=True,
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
        upload_to="verifications",
        null=True,
        blank=True,
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
        upload_to="verifications",
        null=True,
        blank=True,
    )
    pre_service_completion_date = models.DateField(null=True, blank=True)
    added_to_TTP_portal = models.BooleanField(null=True, blank=True)
    contract_code = models.ForeignKey(Contract, on_delete=models.PROTECT, null=True)
    job_title = models.CharField(
        null=True,
        choices=JOB_TITLE.choices,
        default=JOB_TITLE.AIDE,
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return str(self.employee.first_name)

    class Meta:
        db_table = "audit_compliance"
        ordering = ["employee"]
        verbose_name = "Compliance-Auditing Data"
        verbose_name_plural = "Compliance-Auditing Data"
