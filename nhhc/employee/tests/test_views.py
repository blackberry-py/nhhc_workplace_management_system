from unittest.mock import patch

from compliance.models import Compliance, Contract
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from employee.models import Employee
from employee.views import employee_details, hire, reject,  send_new_user_credentials
from model_bakery import baker
from web.models import EmploymentApplicationModel

from nhhc.testing_utils import (
    generate_mock_PhoneNumberField,
    generate_mock_USSocialSecurityNumberField,
    generate_mock_ZipCodeField,
)

baker.generators.add(
    "phonenumber_field.modelfields.PhoneNumberField", generate_mock_PhoneNumberField
)
baker.generators.add("localflavor.us.models.USZipCodeField", generate_mock_ZipCodeField)
baker.generators.add(
    "localflavor.us.models.USSocialSecurityNumberField",
    generate_mock_USSocialSecurityNumberField,
)


class TestEmployeeActions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = baker.make(get_user_model(), username="testuser", password="12345")
        self.accepted_applicant = baker.make(
            EmploymentApplicationModel,
            pk=1,
            last_name="test",
            first_name="new",
            contact_number=generate_mock_PhoneNumberField(),
            email="Dev@gmail.com",
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city="Manhattan",
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
        )
        self.contact = baker.make(Contract, code="FAKE")
        self.staff_user_compliance = baker.make(
            Compliance, employee=self.staff_user, contract_code=self.contact
        )

    def test_hire_employee(self):
        request = self.factory.post("/hire/", {"pk": 1})
        request.user = self.user
        response = hire(request)
        self.assertEqual(response.status_code, 201)

    def test_reject_employee(self):
        request = self.factory.post("/reject/", {"pk": 2})
        request.user = self.user
        response = reject(request)
        self.assertEqual(response.status_code, 204)

    # TODO: FIND WAY TO TEST MAIL SENDING
    # def test_send_new_user_credentials(self):
    #     new_user = self.staff_user
    #     send_new_user_credentials(new_user)
    #     mock_send_mail.assert_called_once()

    def test_employee_details_permission_denied(self):
        request = self.factory.get("/employee/1/")
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            employee_details(request, 1)

    def test_employee_details_staff_user(self):
        request = self.factory.get("/employee/4/")
        request.user = self.staff_user
        response = employee_details(request, 4)
        self.assertEqual(response.status_code, 200)
