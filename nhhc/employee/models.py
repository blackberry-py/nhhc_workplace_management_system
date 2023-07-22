import pendulum
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.us.models import USSocialSecurityNumberField
from localflavor.us.models import USStateField
from localflavor.us.models import USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Employee(AbstractUser):
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
    street_address = models.CharField(max_length=255, default="", null=True, blank=True)
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
    qualifications = models.CharField(
        null=True,
        choices=QUALIFICATIONS.choices,
        default=QUALIFICATIONS.HS_GED,
        max_length=255,
        blank=True,
    )
    in_compliance = models.BooleanField(default=False, null=True)
    onboarded = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"(Employee Id:{self.id}), Name: {self.last_name}, {self.first_name} | Username: {self.username}"

    def onboarding_complete(self):
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
            return True
        else:
            return False

    def generate_random_password(self):
        letters = string.ascii_lowercase
        random_password = "".join(random.choice(letters) for i in range(8))
        return random_password

    class Meta:
        db_table = "employee"
        ordering = ["last_name", "first_name", "-hire_date"]
        verbose_name = "Agency Employee"
        verbose_name_plural = "Agency Employees"
