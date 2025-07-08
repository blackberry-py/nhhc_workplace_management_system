from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField
from django_prometheus.models import ExportModelOperationsMixin
from localflavor.us.models import USStateField, USZipCodeField
from loguru import logger
from phonenumber_field.modelfields import PhoneNumberField
from sage_encrypt.fields.asymmetric import (
    EncryptedCharField,
    EncryptedDateField,
    EncryptedEmailField,
)

from common.upload import UploadHandler


class EmployeeMethodUtility:
    @staticmethod
    def create_unique_username(first_name: str, last_name: str) -> str:
        """
        Create a unique username by adding a number to the end of the username if it's already taken.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.

        Returns:
            str: The unique username for the user.

        Raises:
            IntegrityError: If the username is already taken and no available unique username can be generated.

        """
        last_name = last_name.lower()
        first_name = first_name.lower()
        username = f"{last_name}.{first_name}"
        logger.debug(f"Initial Username: {username}")

        try:
            # Try to create a new user with the given username
            get_user_model().objects.get(username=username)
            max_num = get_user_model().objects.filter(username__startswith=username).count()

            # If no number is currently appended, set the max_num to 0
            if max_num == 1:
                max_num = 0

            # Append the next number to the username and try to create a new user again
            next_username = username + str(max_num)

            # Return the next available username
            logger.debug(f"Inital Username Unavailable. Next Available Username: {next_username}")
            return next_username

        except ObjectDoesNotExist:
            # If no IntegrityError is raised, return the original username
            logger.debug("Inital Username Available")
            return username


class EmployeeManager(EmployeeMethodUtility, BaseUserManager, ExportModelOperationsMixin("employee-manager")):
    """
    Custom user manager
    """

    def create_user(self, password: str, first_name: str, last_name: str, **kwargs) -> User:  # pylint: disable=unused-argument
        """
        Create a new user account with the provided first name, last name, and password.

        Args:
            password (str): The password for the new user account.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            **kwargs: Additional keyword arguments for user creation.

        Returns:
            User: The newly created user object.

        Raises:
            ValueError: If any of the required parameters (password, first_name, last_name) are missing.

        """
        if not password or not first_name or not last_name:
            raise ValueError("We need password \n first name \n and last name to create and account...")
        username = self.create_unique_username(first_name, last_name)
        user = self.model(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        print(f"Successfully Created an account for {first_name} with username {username}")
        return user

    def create_superuser(self, username: str, password: str, email: str, first_name: str = "New", last_name: str = "Admin", **kwargs) -> User:  # pylint: disable=unused-argument
        """
        Create a superuser account with the provided username, password, email, first name, and last name.

        Args:
            username (str): The username for the superuser account.
            password (str): The password for the superuser account.
            email (str): The email address for the superuser account.
            first_name (str, optional): The first name of the superuser. Defaults to "New".
            last_name (str, optional): The last name of the superuser. Defaults to "Admin".
            **kwargs: Additional keyword arguments.

        Returns:
            user (Employees): The created superuser object.

        Raises:
            ValueError: If username, password, first name, or last name are missing.

        """
        if not password or not first_name or not last_name:
            raise ValueError("We need username, \n password \n first name \n and last name to create and account...")
        user = self.create_user(
            password=password,
            username=self.create_unique_username(first_name, last_name),
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


employee_resume_uploads = UploadHandler("resume")
employee_cpr_card_uploads = UploadHandler("cpr_verification")


class Employee(EmployeeMethodUtility, AbstractUser, ExportModelOperationsMixin("employee")):
    """
    Represents an employee in the organization and is the Core User Model

    Attributes:
        employee_id (int): The unique identifier for the employee.
        username (str): The username of the employee.
        gender (str): The gender of the employee.
        language (str): The language spoken by the employee.
        social_security (str): The encrypted social security number of the employee.
        date_of_birth (date): The date of birth of the employee.
        marital_status (str): The marital status of the employee.
        ...

    Methods:
        __str__(self) -> str: Returns a string representation of the employee.
        terminate_employment(self) -> None: Terminates the employment of the employee.
        is_profile_complete(self) -> bool: Checks if the employee's profile is complete.
        create_unique_username(first_name: str, last_name: str) -> str: Creates a unique username for the employee.

    Meta:
        db_table (str): The database table name for the Employee model.
        ordering (list): The default ordering of Employee instances.
        verbose_name (str): The singular name for the Employee model.
        verbose_name_plural (str): The plural name for the Employee model.
        unique_together (list): The unique constraints for the Employee model.
        get_latest_by (str): The field used for retrieving the latest Employee instance.

    """

    objects = EmployeeManager()

    class GENDER(models.TextChoices):
        """
        Enum values representing different gender options.

        Attributes:
            MALE: Represents the Male gender.
            FEMALE: Represents the Female gender.
            NON_GENDERED: Represents a Non-Gendered option.(Default)
            BINARY: Represents the Binary gender option.

        """

        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NON_GENDERED = "X", _("Non-Gendered")
        BINARY = "B", _("Binary")

    class PatientWorkerRelationship(models.TextChoices):
        """
        Enum Values define the relationship between a patient and a worker.

        Attributes:
            RELATED: Represents the case where the worker is related to the patient.
            NOT_RELATED: Represents the case where the worker is not related to the patient.(Default)

        """

        RELATED = "true", _("Yes, I am Related to my patient")
        NOT_RELATED = "false", _("No, I am NOT Related to my patient")

    class MaritalStatus(models.TextChoices):
        """
        Enum values representing marital status choices.

        Attributes:
            MARRIED: Represents the status of being married.
            DIVORCED: Represents the status of being divorced.
            SEPARATED: Represents the status of being separated.
            WIDOWED: Represents the status of being widowed.
            NEVER_MARRIED: Represents the status of never being married.

        """

        MARRIED = "M", _("Married")
        DIVORCED = "D", _("Divorced")
        SEPARATED = "S", _("Separated")
        WIDOWED = "W", _("Widowed")
        NEVER_MARRIED = "NM", _("Never Married")

    class DEPARTMENT(models.TextChoices):
        """
        Enum Values to define choices for department types.

        Attributes:
        - PATIENT_CARE: Represents the department for patient care.
        - ADMIN: Represents the administration department.
        - BILLING: Represents the billing department.
        - OTHER: Represents other types of departments.

        """

        PATIENT_CARE = "PC", _("Patient Care")
        ADMIN = "A", _("Administration")
        BILLING = "B", _("Billing")
        OTHER = "O", _("Other")

    class ETHNICITY(models.TextChoices):
        NON_HISPANIC = "NON-HISPANIC", _("Non-Hispanic/Latino")
        HISPANIC = "HISPANIC", _("Hispanic/Latino")
        UNKNOWN = "UNKNOWN", _("Unknown")
        REFUSED = "REFUSED", _("Prefer Not To Disclose")

    class QUALIFICATIONS(models.TextChoices):
        HS_GED = "HIGH_SCHOOL_GED", _("High School Diploma/GED")
        CNA = "CNA", _("Certified Nursing Assistant (CNA)")
        LPN = "LPN", _("LPN")
        RN = "RN", _("Registered Nurse (RN)")
        EX = "EXPERIENCE", _("Applicable Experience")
        BACHELORS = "BACHELORS", _("Bachelor's degree")
        MASTERS = "MASTERS", _("Master’s degree and above")
        OTHER = "O", _("Other")

    class RACE(models.TextChoices):
        BLACK = "BLACK", _("Black/African American")
        NATIVE_AMERICAN = "NATIVE", _("American Indian/Alaska Native")
        ASIAN = "ASIAN", _("Asian")
        HAWAIIAN = "HAWAIIAN", _("Native Hawaiian/Other Pacific Islander")
        WHITE = "WHITE", _("White/Caucasian")
        OTHER = "OTHER", _("Other Race")
        BI_RACIAL = "BI_RACIAL", _("Two or More Races")
        UNKNOWN = "UNKNOWN", _("Unknown")
        REFUSED = "REFUSED", _("Perfer Not To Disclose")

    class LANGUAGE(models.TextChoices):
        ENGLISH = "ENGLISH", _("English")
        CHINESE = "CHINESE", _("Ethnic Chinese")
        GREEK = "GREEK", _("Greek")
        ITALIAN = "ITALIAN", _("Italian")
        LAOTIAN = "LAOTIAN", _("Laotian")
        ROMANIAN = "ROMANIAN", _("Romanian")
        TAGALOG = "TAGALOG", _("Tagalog")
        YIDDISH = "YIDDISH", _("Yiddish")
        ARABIC = "ARABIC", _("Arabic")
        FARSI = "FARSI", _("Farsi")
        GUJARATI = "GUJARATI", _("Gujarati")
        JAPANESE = "JAPANESE", _("Japanese")
        LITHUANIAN = "LITHUANIAN", _("Lithuanian")
        RUSSIAN = "RUSSIAN", _("Russian")
        UKRANIAN = "UKRANIAN", _("Ukranian")
        YUGOSLAVIAN = "YUGOSLAVIAN", _("Yugoslavian")
        ASSYRIAN = "ASSYRIAN", _("Assyrian")
        FRENCH = "FRENCH", _("French")
        HAITIAN_CREOLE = "CREOLE", _("Haitian Creole")
        MON_KHMER = "MON-KHMER", _("Mon-Khmer")
        MANDARIN = "MANDARIN", _("Mandarin")
        SPANISH = "SPANISH", _("Spanish")
        URDU = "URDU", _("Urdu")
        CANTONESE = "CANTONESE", _("Cantonese")
        GERMAN = "GERMAN", _("German")
        HINDI = "HINDI", _("Hindi")
        KOREAN = "KOREAN", _("Korean")
        POLISH = "POLISH", _("Polish")
        SWEDISH = "SWEDISH", _("Swedish")
        VIETNAMESE = "VIETNAMESE", _("Vietnamese")

    employee_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=False, db_index=True)
    gender = EncryptedCharField(
        max_length=10485760,
        choices=GENDER.choices,
        default=GENDER.NON_GENDERED,
        null=True,
        blank=True,
    )

    language = models.CharField(
        max_length=10485760,
        choices=LANGUAGE.choices,
        blank=True,
        null=True,
        default=LANGUAGE.ENGLISH,
    )
    email = EncryptedEmailField(unique=True, null=True, blank=True)
    social_security = EncryptedCharField(unique=True, null=True, blank=True)
    date_of_birth = EncryptedDateField(null=True, blank=True)
    first_name = EncryptedCharField(max_length=10485760, null=True, blank=True)
    middle_name = EncryptedCharField(max_length=10485760, null=True, blank=True)
    last_name = EncryptedCharField(max_length=10485760, null=True, blank=True)
    street_address1 = EncryptedCharField(max_length=10485760, null=True, blank=True)
    street_address2 = EncryptedCharField(max_length=10485760, null=True, blank=True)
    marital_status = models.CharField(
        max_length=10485760,
        null=True,
        blank=True,
        choices=MaritalStatus.choices,
        default=MaritalStatus.NEVER_MARRIED,
    )
    emergency_contact_first_name = EncryptedCharField(
        max_length=10485760,
        null=True,
        blank=True,
    )
    ethnicity = models.CharField(
        max_length=10485760,
        blank=True,
        choices=ETHNICITY.choices,
        default=ETHNICITY.UNKNOWN,
        null=True,
    )
    emergency_contact_last_name = EncryptedCharField(
        max_length=10485760,
        null=True,
        blank=True,
    )
    race = models.CharField(
        max_length=10485760,
        blank=True,
        choices=RACE.choices,
        default=RACE.UNKNOWN,
        null=True,
    )
    emergency_contact_relationship = EncryptedCharField(
        max_length=10485760,
        null=True,
        blank=True,
    )
    emergency_contact_phone = PhoneNumberField(region="US", null=True, blank=True)
    city = EncryptedCharField(max_length=10485760, null=True, blank=True)
    idoa_agency_policies_attestation = models.FileField(
        upload_to="idoa_agency_policies",
        blank=True,
        default="NONE",
    )
    dhs_i9 = models.FileField(upload_to="i9", blank=True, default="NONE")
    marketing_recruiting_limitations_attestation = models.FileField(upload_to="marketing_recruiting_limitations", blank=True, default="NONE")
    do_not_drive_agreement_attestation = models.FileField(upload_to="do_not_drive_agreement", blank=True, default="NONE")
    job_duties_attestation = models.FileField(upload_to="job_duties", blank=True, default="NONE")
    hca_policy_attestation = models.FileField(upload_to="hca_policy", blank=True, default="NONE")
    irs_w4_attestation = models.FileField(upload_to="irs_w4", blank=True, default="NONE")
    state_w4_attestation = models.FileField(upload_to="state_w4", blank=True, default="NONE")
    idph_background_check_authorization = models.FileField(upload_to="idph_bg_check_auth", blank=True, default="NONE")
    qualifications_verification = models.FileField(upload_to=employee_resume_uploads, default="NONE", blank=True)

    cpr_verification = models.FileField(
        upload_to=employee_cpr_card_uploads,
        default="NONE",
        blank=True,
    )

    family_hca = models.CharField(
        max_length=10485760,
        blank=True,
        null=True,
        choices=PatientWorkerRelationship.choices,
        default=PatientWorkerRelationship.NOT_RELATED,
    )

    phone = PhoneNumberField(null=True)
    state = USStateField(null=True)
    ethnicity = models.CharField(
        null=True,
        choices=ETHNICITY.choices,
        max_length=10485760,
        blank=True,
    )
    sms_contact_agreement = models.BooleanField(null=True, help_text="Please Confirm that You Agree to the SMS Communication ")
    sms_contact_number = PhoneNumberField(null=True)
    zipcode = USZipCodeField(null=True)
    application_id = models.BigIntegerField(unique=True, blank=True, null=True)
    hire_date = CreationDateTimeField()
    termination_date = models.DateField(null=True, blank=True)
    qualifications = models.CharField(
        null=True,
        choices=QUALIFICATIONS.choices,
        default=QUALIFICATIONS.HS_GED,
        max_length=10485760,
        blank=True,
    )
    _date_joined = CreationDateTimeField(db_column="date_joined")
    last_modified = ModificationDateTimeField()

    def __str__(self) -> str:
        return f"(Employee Id:{self.pk}), Name: {self.last_name}, {self.first_name} | Username: {self.username}"

    def terminate_employment(self) -> None:
        self.termination_date = settings.NOW
        self.username = f"{self.username}_TERMINATED"
        self.email = f"{self.email}_TERMINATED"
        self.is_active = False
        self.save()

    @property
    def date_joined(self):
        return self._date_joined

    @date_joined.setter
    def date_joined(self):
        self._date_joined = self.hire_date

    def promote_to_admin(self) -> None:
        self.is_staff = True
        self.is_superuser = True
        self.save()

    def demote_from_admin(self) -> None:
        self.is_staff = True
        self.is_superuser = False
        self.save()

    class Meta:
        db_table = "employee"
        ordering = ["last_name", "first_name", "-hire_date"]
        verbose_name = "Agency Employee"
        verbose_name_plural = "Agency Employees"
        get_latest_by = "-hire_date"
        indexes = [
            models.Index(fields=["username"], name="username_idx"),
            models.Index(fields=["first_name"], name="first_name_idx"),
        ]
