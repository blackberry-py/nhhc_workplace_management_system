from django.db import models
from django.utils.translation import gettext_lazy as _
from employee.models import Employee


# Create your models here.
class Announcements(models.Model):
    class STATUS(models.TextChoices):
        ACTIVE = "A", _("Active")
        DRAFT = "D", _("Draft")
        DELETED = "X", _("Deleted")

    class IMPORTANCE(models.TextChoices):
        SAFETY = "C", _("Safety")
        TRAINING = "T", _("Training")
        COMPLIANCE = "X", _("Compliance")
        GENERAL = "G", _("General")

    message = models.TextField()
    announcement_title = models.CharField(max_length=255, default="")
    posted_by = models.ForeignKey(Employee, on_delete=models.PROTECT)
    date_posted = models.DateTimeField(auto_now=True)
    message_type = models.CharField(
        max_length=255,
        choices=IMPORTANCE.choices,
        default=IMPORTANCE.GENERAL,
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS.choices,
        default=STATUS.DRAFT,
    )

    def post(self):
        self.status = STATUS.ACTIVE

    def delete(self):
        self.status = STATUS.ACTIVE

    def repost(self):
        self.date_posted = now

    class Meta:
        db_table = "announcements"
        ordering = ["-date_posted", "status", "message_type"]
        verbose_name = "Internal Announcement"
        verbose_name_plural = "Internal Announcements"
