"""
Module: nhcc.web.models

This module contains the models needed for the front-end for client interest submissions and employment applications.

ClientInterestSubmission:
- Represents the model for client interest submissions.
- Fields include first_name, last_name, email, contact_number, zipcode, insurance_carrier, desired_service, date_submitted, reviewed, reviewed_by.

EmploymentApplicationModel:
- Represents the model for employment applications.
- Fields include first_name, last_name, contact_number, email, home_address, city, state, zipcode, mobility, prior_experience, ipdh_registered, availability_monday, availability_tuesday, availability_wednesday, availability_thursday, availability_friday, availability_saturday, availability_sunday, reviewed, hired, reviewed_by, date_submitted.

Both models have methods for marking as reviewed, hiring an applicant, and rejecting an applicant.

Note: The module also includes choices for services, mobility, and prior experience.

"""

from datetime import datetime
from typing import Any, Dict

from arrow import Arrow, arrow, get, now
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_prometheus.models import ExportModelOperationsMixin
from employee.models import Employee
from localflavor.us.models import USStateField, USZipCodeField
from loguru import logger
from phonenumber_field.modelfields import PhoneNumberField
from sage_encrypt.fields.asymmetric import EncryptedCharField, EncryptedEmailField

from nhhc.utils.password_generator import RandomPasswordGenerator
from nhhc.utils.upload import UploadHandler

now: Arrow = now(tz="US/Central")


class ClientInterestSubmission(models.Model, ExportModelOperationsMixin("client_inquiries")):
    """
    Model representing client interest submissions.

    Attributes:
        first_name (str): The first name of the client.
        last_name (str): The last name of the client.
        email (str): The email address of the client.
        contact_number (PhoneNumberField): The contact number of the client.
        home_address1 (str): The first line of the client's home address.
        home_address2 (str): The second line of the client's home address.
        city (str): The city of the client's address.
        zipcode (USZipCodeField): The zipcode of the client's address.
        state (USStateField): The state of the client's address.
        insurance_carrier (str): The insurance carrier of the client.
        desired_service (str): The desired service chosen by the client.
        date_submitted (DateTimeField): The date when the submission was made.
        reviewed (bool): Indicates if the submission has been reviewed.
        reviewed_by (ForeignKey): The employee who reviewed the submission.

    Methods:
        __str__(): Returns a formatted string representation of the client submission.
        marked_reviewed(user_id: Employee) -> None: Marks the submission as reviewed by the specified user.

    Meta:
        db_table (str): The database table name for the model.
        ordering (list): The default ordering of records.
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - Submission Date: {datetime.date(self.date_submitted).strftime('%Y-%m-%d')}"

    class SERVICES(models.TextChoices):
        """
        Enum Values the different types of services.

        Attributes:
            - INTERMITTENT: Intermittent Home Care
            - NONMEDICAL: Non-Medical Home Care
            - MEDICAL_SW: Medical Social Work
            - OCCUP_THERAPY: Occupational Therapy
            - PHYS_THERAPY: Physical Therapy
            - OTHER: Other
        """

        INTERMITTENT = "I", _("Intermittent Home Care")
        NONMEDICAL = "NM", _("Non-Medical Home Care")
        MEDICAL_SW = "MSW", _("Medical Social Work")
        OCCUP_THERAPY = "OT", _("Occupational Therapy")
        PHYS_THERAPY = "PT", _("Physical Therapy")
        OTHER = "NA", _("Other")


    first_name = EncryptedCharField(max_length=10485760)
    last_name = EncryptedCharField(max_length=10485760)
    email = EncryptedEmailField(null=True)
    contact_number = PhoneNumberField(region="US")
    home_address1 = EncryptedCharField(max_length=800, null=True)
    home_address2 = EncryptedCharField(max_length=50, null=True, blank=True)
    city = EncryptedCharField(max_length=10485760, null=True, blank=True)
    zipcode = USZipCodeField(null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    insurance_carrier = EncryptedCharField(max_length=10485760)
    desired_service = EncryptedCharField(max_length=10485760, choices=SERVICES.choices)
    date_submitted = CreationDateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(null=True, blank=True, default=False, db_index=True)
    last_modified = ModificationDateTimeField()
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    def marked_reviewed(self, user_id: Employee) -> None:
        """Marks the review as reviewed by the specified user.

        Args:
            user_id (Employee): The ID of the user who reviewed the item.

        Returns:
            None
        """
        self.reviewed = True
        self.reviewed_by = user_id

    class Meta:
        """
        This class defines metadata options for the InterestClient model.
        """

        db_table = "interest_clients"
        ordering = ["last_name", "first_name", "date_submitted"]
        verbose_name = "Interested Client"
        verbose_name_plural = "Interested Clients"


applicant_resume_uploads = UploadHandler("applicant/resume")
applicant_cpr_card_uploads = UploadHandler("applicant/cpr_card")


class EmploymentApplicationModel(models.Model, ExportModelOperationsMixin("applications")):
    """
    Model representing an employment application.

    Attributes:
        first_name (str): The first name of the applicant.
        last_name (str): The last name of the applicant.
        contact_number (PhoneNumberField): The contact number of the applicant.
        email (EmailField): The email address of the applicant.
        home_address1 (str): The first line of the applicant's home address.
        home_address2 (str, optional): The second line of the applicant's home address.
        city (str): The city of the applicant's address.
        state (USStateField): The state of the applicant's address.
        zipcode (USZipCodeField): The ZIP code of the applicant's address.
        mobility (str): The mode of transportation chosen by the applicant.
        prior_experience (str): The level of prior experience of the applicant.
        ipdh_registered (bool): Indicates if the applicant is registered with IPDH.
        availability_monday (bool, optional): Indicates availability on Monday.
        availability_tuesday (bool, optional): Indicates availability on Tuesday.
        availability_wednesday (bool, optional): Indicates availability on Wednesday.
        availability_thursday (bool, optional): Indicates availability on Thursday.
        availability_friday (bool, optional): Indicates availability on Friday.
        availability_saturday (bool, optional): Indicates availability on Saturday.
        availability_sunday (bool, optional): Indicates availability on Sunday.
        reviewed (bool, optional): Indicates if the application has been reviewed.
        hired (bool, optional): Indicates if the applicant has been hired.
        reviewed_by (Employee, optional): The employee who reviewed the application.
        date_submitted (DateTimeField): The date and time when the application was submitted.
        employee_id (BigIntegerField, optional): The ID of the employee.

    Methods:
        hire_applicant(hired_by: Employee) -> Dict[str, str]: Hire a new employee.
        reject_applicant(rejected_by: Employee) -> None: Reject an applicant.

    Meta:
        db_table (str): The name of the database table.
        ordering (list): The default ordering of records.
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.pk}) - Submission Date: {datetime.date(self.date_submitted).strftime('%Y-%m-%d')}"

    class MOBILITTY(models.TextChoices):
        """
        Enum values3 for modes of transportation.

        Attributes:
            CAR: I Have Consistent Access To A Car
            PUBLIC: I Use Public Transportation
            RIDE_SHARE: I Use Rideshare (Uber/Lyft) or a Reliable Pickup/Dropoff Provider
            OTHER: Other
        """

        CAR = "C", _("I Have Consistent Access To A Car")
        PUBLIC = "P", _("I Use Public Transportation")
        RIDE_SHARE = "RS", _(
            "I Use Rideshare (Uber/Lyft) or a Reliable Pickup/Dropoff Provider",
        )
        OTHER = "NA", _("Other")

    class PRIOREXPERIENCE(models.TextChoices):
        """
        Enum Values for values of prior experience.

         Attributes:
             SENIOR: Represents 12+ months of experience.
             JUNIOR: Represents 3+ months of experience.
             NEW: Represents no prior experience.
        """

        SENIOR = "S", _("12+ Months")
        JUNIOR = "J", _("3+ Months")
        NEW = "N", _("No Prior Experience")

    first_name = EncryptedCharField(max_length=10485760)
    last_name = EncryptedCharField(max_length=10485760)
    contact_number = PhoneNumberField(region="US")
    email = EncryptedEmailField(max_length=10485760)
    home_address1 = EncryptedCharField(max_length=10485760)
    home_address2 = EncryptedCharField(max_length=10485760, null=True, blank=True)
    city = EncryptedCharField(
        max_length=10485760,
    )
    state = USStateField(max_length=10485760)
    zipcode = USZipCodeField()
    mobility = models.CharField(max_length=10485760, choices=MOBILITTY.choices)
    prior_experience = models.CharField(max_length=10485760, choices=PRIOREXPERIENCE.choices)
    ipdh_registered = models.BooleanField(default=False)
    availability_monday = models.BooleanField(null=True, blank=True)
    availability_tuesday = models.BooleanField(null=True, blank=True)
    availability_wednesday = models.BooleanField(null=True, blank=True)
    availability_thursday = models.BooleanField(null=True, blank=True)
    availability_friday = models.BooleanField(null=True, blank=True)
    availability_saturday = models.BooleanField(null=True, blank=True)
    availability_sunday = models.BooleanField(null=True, blank=True)
    reviewed = models.BooleanField(null=True, blank=True, default=False, db_index=True)
    hired = models.BooleanField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    date_submitted = CreationDateTimeField()
    last_modified = ModificationDateTimeField()
    employee_id = models.BigIntegerField(blank=True, null=True)
    resume_cv = models.FileField(upload_to=applicant_resume_uploads.generate_randomized_file_name, null=True, blank=True)

    def hire_applicant(self, hired_by: Employee) -> Dict[str, str]:
        """
        Hire a new employee by creating a user account, generating a random password, and saving employee and compliance information in the database.

        Args:
          hired_by (Employee): Instance of the Employee who is hiring the applicant.

        Returns:
            dict: A dictionary containing the auto-generated username, auto-generated password and instance of the user
        Raises:
        Exception: If an error occurs during the hiring process.

        """
        try:
            return self._convert_applicant_to_employee(hired_by)
        except Exception as e:
            log_message = f"Unable to Hire {self.last_name},{self.first_name} - REASON:{e} "
            logger.error(log_message)
            return RuntimeError(e)

    def _convert_applicant_to_employee(self, hired_by: Employee) -> Dict[str, Any]:
        """
        Converts an applicant to an employee by creating a new Employee instance, generating a random password, saving the employee, and updating applicant attributes.

        Args:
            hired_by: The user who hired the applicant.

        Returns:
            dict: A dictionary containing details of the new employee such as user, plain_text_password, username, employee_id, email, first_name, and last_name.
        """
        new_employee = Employee(
            is_superuser=False,
            username=Employee.create_unique_username(self.first_name, self.last_name),
            is_active=True,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            street_address1=self.home_address1,
            street_address2=self.home_address2,
            state=self.state,
            city=self.city,
            zipcode=self.zipcode,
            application_id=self.pk,
            qualifications_verification=self.resume_cv,
        )
        password = RandomPasswordGenerator.generate()
        new_employee.password = make_password(password)
        new_employee.save()
        self.hired = True
        self.reviewed = True
        self.reviewed_by = hired_by
        return {
            "user": new_employee,
            "plain_text_password": password,
            "username": new_employee.username,
            "employee_id": new_employee.employee_id,
            "email": new_employee.email,
            "first_name": new_employee.first_name,
            "last_name": new_employee.last_name,
        }

    def reject_applicant(self, rejected_by: Employee) -> None:
        """Rejects an applicant.

        Args:
            rejected_by (Employee): The employee who rejected the applicant.

        Returns:
            None
        """
        self.hired = False
        self.reviewed = True
        self.reviewed_by = rejected_by
        self.save()

    class Meta:
        """
        This class defines metadata options for the EmploymentApplicationModel model.
        """

        db_table = "employment_interests"
        ordering = ["last_name", "first_name", "date_submitted"]
        verbose_name = "Prospective Employee"
        verbose_name_plural = "Prospective Employees"
