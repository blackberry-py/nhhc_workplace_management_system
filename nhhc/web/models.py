import random
import string

from django.contrib.auth.hashers import make_password
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from icecream import ic
from localflavor.us.models import USStateField
from localflavor.us.models import USZipCodeField
from pendulum import now
from phonenumber_field.modelfields import PhoneNumberField
from compliance.models import Compliance
from employee.models import Employee

now = now(tz="America/Chicago")


class ClientInterestSubmissions(models.Model):
    class SERVICES(models.TextChoices):
        INTERMITTENT = "I", _("Intermittent Home Care")
        NONMEDICAL = "NM", _("Non-Medical Home Care")
        MEDICAL_SW = "MSW", _("Medical Social Work")
        OCCUP_THERAPY = "OT", _("Occupational Therapy")
        PHYS_THERAPY = "PT", _("Physical Therapy")
        OTHER = "NA", _("Other")

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    contact_number = PhoneNumberField(region="US")
    zipcode = USZipCodeField()
    insurance_carrier = models.CharField(max_length=255)
    desired_service = models.CharField(max_length=255, choices=SERVICES.choices)
    date_submitted = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    def marked_reviewed(self, user_id):
        self.reviewed = True
        self.reviewed_by = user_id

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - Submission Date: {self.date_submitted}"

    class Meta:
        db_table = "interest_clients"
        ordering = ["last_name", "first_name", "date_submitted"]
        verbose_name = "Interested Client"
        verbose_name_plural = "Interested Clients"


class EmploymentApplicationModel(models.Model):
    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.id}) - Submitted:{self.date_submitted}"

    class MOBILITTY(models.TextChoices):
        CAR = "C", _("I Have Consistent Access To A Car")
        PUBLIC = "P", _("I Use Public Transportation")
        RIDE_SHARE = "RS", _(
            "I Use Rideshare (Uber/Lyft) or a Reliable Pickup/Dropoff Provider",
        )
        OTHER = "NA", _("Other")

    class PRIOREXPERIENCE(models.TextChoices):
        SENIOR = "S", _("12+ Months")
        JUNIOR = "J", _("3+ Months")
        NEW = "N", _("No Prior Experience")

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = PhoneNumberField(region="US")
    email = models.EmailField(max_length=254)
    home_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = USStateField(max_length=2)
    zipcode = USZipCodeField()
    mobility = models.CharField(max_length=255, choices=MOBILITTY.choices)
    prior_experience = models.CharField(max_length=255, choices=PRIOREXPERIENCE.choices)
    ipdh_registered = models.BooleanField(default=False)
    availability_monday = models.BooleanField(null=True, blank=True)
    availability_tuesday = models.BooleanField(null=True, blank=True)
    availability_wednesday = models.BooleanField(null=True, blank=True)
    availability_thursday = models.BooleanField(null=True, blank=True)
    availability_friday = models.BooleanField(null=True, blank=True)
    availability_saturday = models.BooleanField(null=True, blank=True)
    availability_sunday = models.BooleanField(null=True, blank=True)
    reviewed = models.BooleanField(null=True, blank=True, default=False)
    hired = models.BooleanField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    date_submitted = models.DateTimeField(auto_now_add=True)

    def generate_random_password(self):
        letters = string.ascii_lowercase
        random_password = "".join(random.choice(letters) for i in range(8))
        return random_password

    def hire(self, hired_by):
        username = (
            f"{self.first_name.lower()}.{self.last_name.lower().replace(' ', '.')}"
        )
        ic(username)
        new_employee = Employee(
            is_superuser=False,
            username=username,
            is_active=True,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.contact_number,
        )
        password = self.generate_random_password()
        new_employee.password = make_password(password)
        new_employee.save()
        compliance = Compliance(employee=new_employee)
        compliance.save()
        self.hired = True
        self.reviewed = True
        self.reviewed_by = hired_by

    def reject(self, rejected_by):
        self.hired = False
        self.reviewed = True
        self.reviewed_by = rejected_by

    class Meta:
        db_table = "employment_interests"
        ordering = ["last_name", "first_name", "date_submitted"]
        verbose_name = "Prospective Employee"
        verbose_name_plural = "Prospective Employees"
