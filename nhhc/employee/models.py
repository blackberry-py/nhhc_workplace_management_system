from authentication.models import RandomPasswordGenerator
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import IntegrityError, models, transaction
from django.db.models import Max
from django.db.models.functions import Cast, Substr
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from localflavor.us.models import (
    USSocialSecurityNumberField,
    USStateField,
    USZipCodeField,
)
from phonenumber_field.modelfields import PhoneNumberField
from loguru import logger   
from django.conf import settings
import arrow

logger.add(settings.DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(settings.PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(settings.LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")

now = str(arrow.now().format('YYYY-MM-DD'))
class EmployeeManager(BaseUserManager):
    """
    Custom user manager
    """
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

        Example:
            create_unique_username("John", "Doe")
        """
        last_name = last_name.lower()
        first_name = first_name.lower()
        username = f"{last_name}.{first_name}"
        logger.debug(f"Inital Username: {username}")

        try:
            # Try to create a new user with the given username
            user = get_user_model().objects.get(username=username)
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
            logger.deug(f"Inital Username Available")
            return username

            

    def create_user(self, password, first_name, last_name, **kwargs):
        if not password or not first_name or not last_name:
            raise ValueError(
                "We need password \n first name \n and last name to create and account..."
            )
        username = self.create_unique_username(first_name, last_name)
        user = self.model(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        print(
            f"Successfully Created an account for {first_name} with username {username}"
        )
        return user

    def create_superuser(self, username, password, email, first_name="New", last_name="Admin", **kwargs):
        if not password or not first_name or not last_name:
            raise ValueError(
                "We need username, \n password \n first name \n and last name to create and account..."
            )
        user = self.create_user(
            password=password,
            username=self.create_unique_username(first_name, last_name),
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class Employee(AbstractUser, ExportModelOperationsMixin("employee")):
    objects = EmployeeManager()

    class GENDER(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NON_GENDERED = "X", _("Non-Gendered")
        BINARY = "B", _("Binary")

    class PATIENT_WORKER_RELATIONSHIP(models.TextChoices):
        RELATED = "true", _("Yes, I am Related to my patient")
        NOT_RELATED = "false", _("No, I am NOT Related to my patient")

    class MARITAL_STATUS(models.TextChoices):
        MARRIED = "M", _("Married")
        DIVORCED = "D", _("Divorced")
        SEPARATED = "S", _("Separated")
        WIDOWED = "W", _("Widowed")
        NEVER_MARRIED = "NM", _("Never Married")

    class DEPARTMENT(models.TextChoices):
        PATIENT_CARE = "PC", _("Patient Care")
        ADMIN = "A", _("Administration")
        BILLING = "B", _("Billing")
        OTHER = "O", _("Other")

    class ETHNICITY(models.TextChoices):
        NON_HISPANIC = "NON-HISPANIC", _("Non-Hispanic/Latino")
        HISPANIC = "HISPANIC", _("Hispanic/Latino")
        UNKNOWN = "UNKNOWN", _("Unknown")
        REFUSED = "REFUSED", _("Perfer Not To Disclose")

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

    gender = models.CharField(
        max_length=255,
        choices=GENDER.choices,
        default=GENDER.NON_GENDERED,
        null=True,
        blank=True,
    )

    language = models.CharField(
        max_length=255,
        choices=LANGUAGE.choices,
        blank=True,
        null=True,
        default=LANGUAGE.ENGLISH,
    )
    social_security = USSocialSecurityNumberField(unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    middle_name = models.CharField(max_length=255, default="", null=True, blank=True)
    street_address1 = models.CharField(
        max_length=255, default="", null=True, blank=True
    )
    street_address2 = models.CharField(
        max_length=255, default="", null=True, blank=True
    )
    marital_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=MARITAL_STATUS.choices,
        default=MARITAL_STATUS.NEVER_MARRIED,
    )

    emergency_contact_first_name = models.CharField(
        max_length=255,
        default="",
        null=True,
        blank=True,
    )
    ethnicity = models.CharField(
        max_length=255,
        blank=True,
        choices=ETHNICITY.choices,
        default=ETHNICITY.UNKNOWN,
        null=False,
    )
    emergency_contact_last_name = models.CharField(
        max_length=255,
        default="",
        null=True,
        blank=True,
    )
    race = models.CharField(
        max_length=255,
        blank=True,
        choices=RACE.choices,
        default=RACE.UNKNOWN,
        null=False,
    )
    emergency_contact_relationship = models.CharField(
        max_length=255,
        default="",
        null=True,
        blank=True,
    )
    emergency_contact_phone = PhoneNumberField(region="US", null=True, blank=True)
    city = models.CharField(max_length=255, default="", null=True, blank=True)

    qualifications_verification = models.FileField(
        upload_to="verifications",
        null=True,
        blank=True,
    )
    cpr_verification = models.FileField(
        upload_to="verifications",
        null=True,
        blank=True,
    )

    family_hca = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=PATIENT_WORKER_RELATIONSHIP.choices,
        default=PATIENT_WORKER_RELATIONSHIP.NOT_RELATED,
    )

    phone = PhoneNumberField(null=True)
    state = USStateField(null=True)
    ethnicity = models.CharField(
        null=True,
        choices=ETHNICITY.choices,
        max_length=255,
        blank=True,
    )
    zipcode = USZipCodeField(null=True)

    hire_date = models.DateField(auto_now=True)
    termination_date = models.DateField(null=True, blank=True)
    qualifications = models.CharField(
        null=True,
        choices=QUALIFICATIONS.choices,
        default=QUALIFICATIONS.HS_GED,
        max_length=255,
        blank=True,
    )
    in_compliance = models.BooleanField(default=False, null=True)
    onboarded = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"(Employee Id:{self.id}), Name: {self.last_name}, {self.first_name} | Username: {self.username}"
    
    def terminate_employment(self):
        self.termination_date = now
        self.username = self.username + "X"
        self.is_active = False
        self.save()
        
    def complete_onboarding(self) -> bool:
        """
        This method checks if all required fields for onboarding are filled out and marks the user as onboarded if so.
        Args:
            self: The instance of the class.

        Returns:
            bool: True if all required fields are filled out, False otherwise.
            
        """
        valid_fields = 0
        fields_to_be_validated = [
            self.social_security,
            self.gender,
            self.city,
            self.phone,
            self.state,
            self.street_address,
            self.zipcode,
            self.emergency_contact_relationship,
            self.emergency_contact_last_name,
            self.emergency_contact_first_name,
            self.marital_status,
        ]
        for field in fields_to_be_validated:
            if field is not None or field != " ":
                valid_fields += 1

        if valid_fields == 10:
            self.onboarded = now
            self.save()
            return True
        else:
            return False

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
        logger.debug(f"Inital Username: {username}")

        try:
            # Try to create a new user with the given username
            user = get_user_model().objects.get(username=username)
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
            logger.debug(f"Inital Username Available")
            return username

    class Meta:
        db_table = "employee"
        ordering = ["last_name", "first_name", "-hire_date"]
        verbose_name = "Agency Employee"
        verbose_name_plural = "Agency Employees"
        get_latest_by="-date_joined"
