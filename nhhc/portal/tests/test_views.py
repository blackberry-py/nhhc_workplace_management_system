import json
import random
from unittest.mock import MagicMock, patch

from compliance.models import Compliance, Contract
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from employee.forms import EmployeeForm
from employee.models import Employee
from faker import Faker
from loguru import logger
from model_bakery import baker
from portal.views import (
    ClientInquiriesListView,
    EmploymentApplicationListView,
    marked_reviewed,
)
from web.models import ClientInterestSubmission, EmploymentApplicationModel

from nhhc.utils.testing import (
    generate_mock_PhoneNumberField,
    generate_mock_USSocialSecurityNumberField,
    generate_mock_ZipCodeField,
)

dummy_data = Faker()


baker.generators.add("phonenumber_field.modelfields.PhoneNumberField", generate_mock_PhoneNumberField)
baker.generators.add("localflavor.us.models.USZipCodeField", generate_mock_ZipCodeField)
baker.generators.add(
    "localflavor.us.models.USSocialSecurityNumberField",
    generate_mock_USSocialSecurityNumberField,
)


class ProfileTestCase(TestCase):
    @override_settings(STORAGE_DESTINATION="testing")
    def setUp(self):
        self.client = Client()
        self.employee = baker.make(
            Employee,
            username="testuser",
            password="testpassword",
            is_superuser=True,
            is_staff=True,
        )
        self.contract = baker.make(Contract)
        self.compliance = baker.make(Compliance, employee=self.employee)

    def test_profile_get_method(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(f"/profile/{self}")
        self.assertEqual(response.status_code, 200)  # Check if the get request is successful

    def test_profile_form(self):
        self.client.force_login(Employee)
        form_data = {
            "gender": random.choice(["M", "F", "X", "B"]),
            "social_security": dummy_data.ssn(),
            "middle_name": dummy_data.first_name(),
            "street_address": dummy_data.address(),
            "last_name": dummy_data.last_name(),
            "first_name": dummy_data.first_name(),
            "marital_status": random.choice(["M", "D", "S", "W", "NM"]),
            "emergency_contact_first_name": dummy_data.first_name(),
            "emergency_contact_last_name": dummy_data.last_name(),
            "emergency_contact_relationship": random.choice(["spouse", "parent", "sibiling"]),
            "emergency_contact_phone": "+17087561321",
            "city": dummy_data.city(),
            "email": dummy_data.profile()["mail"],
            "phone": "+17087561321",
            "state": dummy_data.state_abbr(),
            "zipcode": dummy_data.postcode_in_state(),
            "ethnicity": random.choice(["REFUSED", "HISPANIC", "NON-HISPANIC", "UNKNOWN"]),
            "family_hca": random.choice(["true", "false"]),
            "username": dummy_data.profile()["username"],
            "date_of_birth": dummy_data.profile()["birthdate"],
            "contract_code": self.contract,
        }
        form = EmployeeForm(data=form_data, instance=self.employee)
        if form.errors:
            print(form.errors)
        else:
            self.assertTrue(form.is_valid())  # Check if the form is valid

    def test_profile_edge_cases(self):
        # TODO: Add edge cases testing here
        pass


class ClientInquiriesTestCase(TestCase):
    @override_settings(
        STORAGE_DESTINATION="testing",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="pWxH7dzX",
    )
    def setUp(self):
        self.submission1 = baker.make(
            ClientInterestSubmission,
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            reviewed=False,
        )
        self.submission2 = baker.make(
            ClientInterestSubmission,
            email="janesmith@example.com",
            reviewed=True,
        )
        self.client = Client()
        self.employee = baker.make(
            Employee,
            username="testuser",
            password="testpassword",
            is_staff=True,
            is_superuser=False,
        )
        self.contract = baker.make(Contract)
        self.compliance = baker.make(Compliance, employee=self.employee)

    def test_all_client_inquiries(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("inquiries"))
        self.assertEqual(response.status_code, 200)


class SubmissionDetailTestCase(TestCase):
    @override_settings(STORAGE_DESTINATION="testing")
    def setUp(self):
        self.submission = ClientInterestSubmission.objects.create(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            contact_number="1234567890",
            zipcode="12345",
            insurance_carrier="ABC Insurance",
            desired_service="Service A",
            date_submitted="2022-01-01",
            reviewed=False,
            reviewed_by=None,
        )

    def test_submission_detail_view(self):
        url = reverse("client_interest_details", kwargs={"pk": self.submission.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, "Client Interest")
        self.assertContains(response, "John")
        self.assertContains(response, "Doe")
        # Add more assertions for other fields


class MarkedReviewedTestCase(TestCase):
    def setUp(self):
        self.submission = baker.make(ClientInterestSubmission)
        self.client = Client()
        self.user = baker.make(
            Employee,
            username="testuser",
            password="12345",
            is_staff=False,
            is_superuser=False,
            application_id=random.randint(2, 5655),
        )
        self.staff_user = baker.make(
            Employee,
            username="staffuser",
            password="12345",
            is_staff=True,
            is_superuser=True,
            application_id=random.randint(2, 5655),
        )
        self.application = baker.make(EmploymentApplicationModel)

    def test_marked_reviewed_view_invalid_json(self):
        mock_request = MagicMock()
        mock_request.body = "invalid json"

        response = marked_reviewed(mock_request)
        self.assertEqual(response.status_code, 400)

    def test_marked_reviewed_view_object_does_not_exist(self):
        mock_request = MagicMock()
        mock_request.body = json.dumps({"pk": 999})  # Assuming pk 999 does not exist

        response = marked_reviewed(mock_request)
        self.assertEqual(response.status_code, 400)

    @patch("home.views.logger")
    def test_marked_reviewed_view_exception(self, mock_logger):
        mock_request = MagicMock()
        mock_request.body = json.dumps({"pk": self.submission.pk})
        mock_request.user = MagicMock()
        mock_logger.error = MagicMock()

        with patch("home.views.ClientInterestSubmission.objects.get") as mock_get:
            mock_get.side_effect = Exception("Some error")

            response = marked_reviewed(mock_request)
            self.assertEqual(response.status_code, 500)
            mock_logger.error.assert_called_once()
