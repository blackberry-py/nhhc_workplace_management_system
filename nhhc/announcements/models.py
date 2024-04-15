import arrow
from django.db import models
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from employee.models import Employee
from loguru import logger

now = arrow.utcnow()


# Create your models here.
class Announcements(models.Model, ExportModelOperationsMixin("announcements")):
    class STATUS(models.TextChoices):
        ACTIVE = "A", _(message="Active")
        DRAFT = "D", _(message="Draft")
        ARCHIVE = "X", _(message="Archived")

    class IMPORTANCE(models.TextChoices):
        SAFETY = "C", _(message="Safety")
        TRAINING = "T", _(message="Training")
        COMPLIANCE = "X", _(message="Compliance")
        GENERAL = "G", _(message="General")

    message = models.TextField()
    announcement_title = models.CharField(max_length=255, default="")
    posted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
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


def post(self, request: HttpRequest) -> None:
    """
    Method to post an annoucement instance.

    Args:
    - request: HttpRequest object containing the request data

    Returns:
    - None

    This method sets the 'posted_by' attribute to the user id from the request,
    sets the 'status' attribute to 'ACTIVE', saves the object, and logs the success or error message.
    """
    try:
        self.posted_by = request.user.id
        self.status = STATUS.ACTIVE
        self.save()
        logger.success(f"Succesfully posted {self.id}")
    except Exception as e:
        logger.error(f"ERROR: Unable to post {self.id} - {e}")


def archive(self) -> None:
    """
    Method to delete an annoucement instance.

    This method sets the status of the object to 'ARCHIVE', saves the object, and logs a success message if successful.
    If an exception occurs during the deletion process, an error message is logged.
    """
    try:
        self.status = STATUS.ARCHIVE
        self.save()
        logger.success(f"Succesfully deleted {self.id}")
    except Exception as e:
        logger.error(f"ERROR: Unable to delete {self.id} - {e}")


def repost(self) -> None:
    """
    Reposts an annoucemen t post by updating the date_posted, status, and saving the changes.

    Parameters:
    - self: the current instance of the post

    Returns:
    - None

    Logs a success message if the repost is successful, otherwise logs an error message.
    """
    try:
        self.date_posted = now
        self.status = STATUS.ACTIVE
        self.save()
        logger.success(f"Succesfully reposted {self.id}")
    except Exception as e:
        logger.error(f"ERROR: Unable to repost {self.id} - {e}")

    class Meta:
        db_table = "announcements"
        ordering = ["-date_posted", "status", "message_type"]
        verbose_name = "Internal Announcement"
        verbose_name_plural = "Internal Announcements"
