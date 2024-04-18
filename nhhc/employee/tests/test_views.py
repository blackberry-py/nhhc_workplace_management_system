import random
from unittest.mock import patch

from compliance.models import Compliance, Contract
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from employee.models import Employee
from employee.views import employee_details, hire, reject, send_new_user_credentials
from faker import Faker
from loguru import logger
from model_bakery import baker
from web.models import EmploymentApplicationModel

from nhhc.utils.testing import (
    generate_mock_PhoneNumberField,
    generate_mock_USSocialSecurityNumberField,
    generate_mock_ZipCodeField,
)

baker.generators.add("phonenumber_field.modelfields.PhoneNumberField", generate_mock_PhoneNumberField)
baker.generators.add("localflavor.us.models.USZipCodeField", generate_mock_ZipCodeField)
baker.generators.add(
    "localflavor.us.models.USSocialSecurityNumberField",
    generate_mock_USSocialSecurityNumberField,
)
mock_data = Faker()


class TestHireFunction(TestCase):
    def setup(self):
        self.client = Client()
        self.admin_user = baker.make(
            Employee,
            is_superuser=True,
            is_staff=True,
            password="12345",
            application_id=random.randint(2, 5655),
        )
        self.non_admin_user = baker.make(
            Employee,
            is_superuser=False,
            is_staff=True,
            password="12345",
            application_id=random.randint(2, 5655),
        )
        # self.application_to_hire = baker.make(EmploymentApplicationModel, p\=1)

    def test_user_not_authenticated(self):
        response = self.client.post(reverse("hire-employee"), {"pk": "1"})
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 401)

    def test_non_admin_hire(self):
        non_admin = baker.make(Employee, is_superuser=False, is_staff=True)
        application_to_hire = baker.make(
            EmploymentApplicationModel,
            pk=1,
            last_name=mock_data.last_name(),
            first_name=mock_data.first_name(),
            contact_number=generate_mock_PhoneNumberField(),
            email=mock_data.email(),
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city=mock_data.city(),
            state="NY",
            zipcode=generate_mock_ZipCodeField(),
            mobility="C",
            prior_experience="J",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=False,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=False,
        )
        response = self.client.force_login(non_admin)
        response = self.client.post(reverse("hire-employee"), {"pk": "1"})

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 403)

    def test_admin_hire(self):
        admin = baker.make(Employee, is_superuser=True, is_staff=True)
        application_to_hire = baker.make(
            EmploymentApplicationModel,
            pk=1,
            last_name=mock_data.last_name(),
            first_name=mock_data.first_name(),
            contact_number=generate_mock_PhoneNumberField(),
            email=mock_data.email(),
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city=mock_data.city(),
            state="NY",
            zipcode=generate_mock_ZipCodeField(),
            mobility="C",
            prior_experience="J",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=False,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=False,
        )
        request = self.client.force_login(admin)
        response = self.client.post(reverse("hire-employee"), {"pk": "1"})

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 201)

    def test_invalid_pk_value(self):
        admin = baker.make(Employee, is_superuser=True, is_staff=True)
        application_to_hire = baker.make(
            EmploymentApplicationModel,
            pk=1,
            last_name=mock_data.last_name(),
            first_name=mock_data.first_name(),
            contact_number=generate_mock_PhoneNumberField(),
            email=mock_data.email(),
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city=mock_data.city(),
            state="NY",
            zipcode=generate_mock_ZipCodeField(),
            mobility="C",
            prior_experience="J",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=False,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=False,
        )
        request = self.client.force_login(admin)
        response = self.client.post(reverse("hire-employee"), {"pk": "TEST"})

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 400)

    def test_employment_application_not_found(self):
        admin = baker.make(
            Employee,
            first_name=mock_data.first_name(),
            last_name=mock_data.last_name(),
            email=mock_data.email(),
            is_superuser=True,
            is_staff=True,
        )
        request = self.client.force_login(admin)
        response = self.client.post(reverse("hire-employee"), {"pk": "99"})

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 404)

    #


class TestEmployeeActions(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = baker.make(
            Employee,
            password="12345",
            application_id=random.randint(2, 5655),
        )
        self.accepted_applicant = baker.make(
            EmploymentApplicationModel,
            pk=1,
            last_name=mock_data.last_name(),
            first_name=mock_data.first_name(),
            contact_number=generate_mock_PhoneNumberField(),
            email=mock_data.email(),
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city=mock_data.city(),
            state="NY",
            zipcode=generate_mock_ZipCodeField(),
            mobility="C",
            prior_experience="J",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=False,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=False,
        )
        self.rejected_applicant = baker.make(EmploymentApplicationModel, pk=2)
        self.staff_user = baker.make(
            Employee,
            is_superuser=False,
            id=4,
            username="staffuser",
            password="12345",
            is_staff=True,
            application_id=random.randint(2, 5655),
        )
        self.admin = baker.make(
            Employee,
            is_superuser=True,
            id=4,
            username="admin",
            password="12345",
            is_staff=True,
            application_id=random.randint(2, 5655),
        )
        self.contact = baker.make(Contract, code="FAKE")
        self.user_compliance = baker.make(Compliance, employee=self.user, contract_code=self.contact)

    def test_reject_employeen_non_admin(self):
        request = self.client.post("/reject/", {"pk": self.rejected_applicant.pk})
        request.user = self.admin
        response = reject(request)
        self.assertEqual(response.status_code, 405)

    # FIXME: FIND WAY TO TEST MAIL SENDING
    # def test_send_new_user_credentials(self):
    #     new_user = self.staff_user
    #     send_new_user_credentials(new_user)
    #     mock_send_mail.assert_called_once()

    # FIXME: FIND WAY TO TEST MAIL SENDING
    # def test_employee_details_permission_denied(self):
    #     request = self.client.get(f"/employee/{self.user.employee_id}")
    #         request.user = self.staff_user
    #         with self.assertRaises(PermissionDenied):
    #             employee_details(request, self.user.employee_id)

    # FIXME: Resolve Test
    # def test_employee_details_staff_user(self):
    #     client = self.client
    #     client.force_login(self.staff_user)
    #     request = client.get(f"/employee/{self.accepted_applicant.pk}")
    #     logger.debug(request)
    #     response = employee_details(request, pk=self.accepted_applicant.pk)
    #     logger.debug(response)
    #     self.assertEqual(response.status_code, 301)
