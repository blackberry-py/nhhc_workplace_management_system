"""
Module: apps.announcements.models

This module defines a Django model for managing internal announcements within the system.
It includes attributes for message content, announcement title, user who posted the announcement, date posted, message type, and status.
The model provides methods for posting, archiving, and re-posting announcements.

Attributes:
- message: TextField - The content of the announcement.
- announcement_title: CharField - The title of the announcement.
- posted_by: ForeignKey to Employee - The user who posted the announcement.
- date_posted: DateTimeField - The date and time when the announcement was posted.
- message_type: CharField - The type of announcement (choices: SAFETY, TRAINING, COMPLIANCE, GENERAL).
- status: CharField - The status of the announcement (choices: ACTIVE, DRAFT, ARCHIVE).

Methods:
- post(request: HttpRequest) -> None: Method to post an announcement instance.
- archive() -> None: Method to delete an announcement instance.
- repost() -> None: Method to re-post an announcement instance.

Meta:
- db_table: "announcements"
- ordering: ["-date_posted", "status", "message_type"]
- verbose_name: "Internal Announcement"
- verbose_name_plural: "Internal Announcements"

"""

from django.conf import settings
from django.db import models
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from loguru import logger

from applications.employee.models import Employee


class Announcements(models.Model, ExportModelOperationsMixin("announcements")):
    """
    Model representing internal announcements within the system.

    Attributes:
    - message: TextField - The content of the announcement.
    - announcement_title: CharField - The title of the announcement.
    - posted_by: ForeignKey to Employee - The user who posted the announcement.
    - date_posted: DateTimeField - The date and time when the announcement was posted.
    - message_type: CharField - The type of announcement (choices: SAFETY, TRAINING, COMPLIANCE, GENERAL).
    - status: CharField - The status of the announcement (choices: ACTIVE, DRAFT, ARCHIVE).

    Methods:
    - post(request: HttpRequest) -> None: Method to post an announcement instance.
    - archive() -> None: Method to delete an announcement instance.
    - update() -> None: Method to update an announcement instance.

    Meta:
    - db_table: "announcements"
    - ordering: ["-date_posted", "status", "message_type"]
    - verbose_name: "Internal Announcement"
    - verbose_name_plural: "Internal Announcements"

    """

    class STATUS(models.TextChoices):
        """
        Enum Values for the status field.

        Attributes:
            ACTIVE: Represents an active status.
            DRAFT: Represents a draft status.
            ARCHIVE: Represents an archived status.

        """

        ACTIVE = "A", _(message="Active")
        DRAFT = "D", _(message="Draft")
        ARCHIVE = "X", _(message="Archived")

    class IMPORTANCE(models.TextChoices):
        """
        Enum Values for the type of announcement field.

        Attributes:
            SAFETY: Represents an High - SAFETY related Type.
            TRAINING: Represents a Medium  - Training Type.
            COMPLIANCE: Represents an Regulatory Type.
            GENERAL: Represents an General Type.

        """

        SAFETY = "C", _(message="Safety")
        TRAINING = "T", _(message="Training")
        COMPLIANCE = "X", _(message="Compliance")
        GENERAL = "G", _(message="General")

    message = models.TextField()
    announcement_title = models.CharField(max_length=10485760, default="")
    posted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    date_posted = models.DateTimeField(auto_now=True)
    message_type = models.CharField(
        max_length=10485760,
        choices=IMPORTANCE.choices,
        default=IMPORTANCE.GENERAL,
    )
    status = models.CharField(max_length=10485760, choices=STATUS.choices, default=STATUS.DRAFT, db_index=True)

    def __str__(self) -> str:
        return f"{self.announcement_title} ({self.status} - {self.posted_by.last_name}, {self.posted_by.first_name})"

    def post(self, request: HttpRequest) -> None:
        """
        Method to post an announcement instance.

        Args:
            request: HttpRequest object containing the request data

        Returns:
            None

        This method sets the 'posted_by' attribute to the user id from the request,
        sets the 'status' attribute to 'ACTIVE', saves the object, and logs the success or error message.

        """
        try:
            self.posted_by = request.user.employee_id
            self.status = "A"
            self.save()
            logger.success(f"Successfully posted {self.pk}")
        except Exception as e:
            if self.pk is None:
                logger.error(f"ERROR: Unable to post - ID is unavailable - Post Contents: (message:{self.message}, Error: {e})")
            logger.error(f"ERROR: Unable to post {self.pk} - {e}")

    def create_draft(self, request: HttpRequest) -> None:
        """
        Method to create a draft version of an announcement instance.

        Args:
            request: HttpRequest object containing the request data

        Returns:
            None

        This method sets the 'posted_by' attribute to the user id from the request,
        sets the 'status' attribute to 'DRAFT', saves the object, and logs the success or error message.

        """
        try:
            self.posted_by = request.user.employee_id
            self.status = "D"
            self.save()
            logger.success(f"Successfully posted {self.pk}")
        except Exception as e:
            if self.pk is None:
                logger.error(f"ERROR: Unable to Create Draft  - ID is unavailable - Post Contents: (message:{self.message}, Error: {e})")
                settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to Create Draft  - ID is unavailable - Post Contents: (message:{self.message}, Error: {e})")
            logger.error(f"ERROR: Unable to Create Draft  {self.pk} - {e}")
            settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to Create Draft  {self.pk} - {e}")

    def archive(self) -> None:
        """
        Method to delete an announcement instance.

        This method sets the status of the object to 'ARCHIVE', saves the object, and logs a success message if successful.
        If an exception occurs during the deletion process, an error message is logged.
        """
        try:
            self.status = "X"
            self.save()
            logger.success(f"Successfully deleted {self.pk}")
        except Exception as e:
            settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to delete {self.pk} - {e}")
            logger.error(f"ERROR: Unable to delete {self.pk} - {e}")

    def update(self, announcement_title, message, message_type, status) -> None:
        """
        Updates all attributes of Announcement Instance  and saves the changes.

        Args:
            announcement_title: The title of the announcement
            message: The content of the announcement
            message_type: The type of announcement
            status: The status of the announcement

        Returns:
            None

        Logs a success message if the re-post is successful, otherwise logs an error message.

        """
        try:
            self.message = message
            self.announcement_title = announcement_title
            self.message_type = message_type
            self.date_posted = settings.NOW
            self.status = status
            self.save()
            logger.success(f"Successfully re-posted {self.pk}")
        except Exception as e:
            settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to re-post {self.pk} - {e}")
            logger.error(f"ERROR: Unable to re-post {self.pk} - {e}")

    class Meta:
        db_table = "announcements"
        ordering = ["-date_posted", "status", "message_type"]
        verbose_name = "Internal Announcement"
        verbose_name_plural = "Internal Announcements"
