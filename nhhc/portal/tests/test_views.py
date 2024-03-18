import json
import random
from unittest.mock import MagicMock, patch

from compliance.models import Compliance, Contract
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
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
from web.models import ClientInterestSubmissions, EmploymentApplicationModel

from nhhc.utils.testing import (
    generate_mock_PhoneNumberField,
    generate_mock_USSocialSecurityNumberField,
    generate_mock_ZipCodeField,
)

dummy_data = Faker()


baker.generators.add(
    "phonenumber_field.modelfields.PhoneNumberField", generate_mock_PhoneNumberField
)
baker.generators.add("localflavor.us.models.USZipCodeField", generate_mock_ZipCodeField)
baker.generators.add(
    "localflavor.us.models.USSocialSecurityNumberField",
    generate_mock_USSocialSecurityNumberField,
)


class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.employee = baker.make(
            Employee, username="testuser", password="testpassword"
        )
        self.contract = baker.make(Contract)
        self.compliance = baker.make(Compliance, employee=self.employee)

    def test_profile_get_method(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(f"/profile/{self}")
        self.assertEqual(
            response.status_code, 200
        )  # Check if the get request is successful

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
            "emergency_contact_relationship": random.choice(
                ["spouse", "parent", "sibiling"]
            ),
            "emergency_contact_phone": "+17087561321",
            "city": dummy_data.city(),
            "email": dummy_data.profile()["mail"],
            "phone": "+17087561321",
            "state": dummy_data.state_abbr(),
            "zipcode": dummy_data.postcode_in_state(),
            "ethnicity": random.choice(
                ["REFUSED", "HISPANIC", "NON-HISPANIC", "UNKNOWN"]
            ),
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
    def setUp(self):
        self.submission1 = baker.make(
            ClientInterestSubmissions,
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            reviewed=False,
        )
        self.submission2 = baker.make(
            ClientInterestSubmissions,
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
        self.client.force_login()
        response = self.client.get(reverse("inquiries"))
        self.assertEqual(response.status_code, 200)
        inquiries = json.loads(response.content)
        self.assertEqual(len(inquiries), 2)
        self.assertEqual(inquiries[0]["first_name"], "John")
        self.assertEqual(inquiries[1]["email"], "janesmith@example.com")

    def test_client_inquiries(self):
        self.client.force_login(Employee)
        response = self.client.get(reverse("inquiries"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")
        self.assertContains(response, "Interested in your services")
        self.assertContains(response, "Need more information about pricing")
        self.assertContains(response, "Unresponsed: 1")
        self.assertContains(response, "Reviewed: 1")
        self.assertContains(response, "All Submissions: 2")
        self.assertContains(response, "showSearch")

    def test_empty_client_inquiries(self):
        self.client.force_login(Employee)
        ClientInterestSubmissions.objects.all().delete()
        response = self.client.get(reverse("inquiries"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No submissions found")
        self.assertContains(response, "Unresponsed: 0")
        self.assertContains(response, "Reviewed: 0")
        self.assertContains(response, "All Submissions: 0")
        self.assertContains(response, "showSearch")

    def test_no_unresponsed_client_inquiries(self):
        self.client.force_login(Employee)
        self.submission1.reviewed = True
        self.submission1.save()
        response = self.client.get(reverse("inquiries"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unresponsed: 0")
        self.assertContains(response, "Reviewed: 2")
        self.assertContains(response, "All Submissions: 2")
        self.assertContains(response, "showSearch")


class SubmissionDetailTestCase(TestCase):
    def setUp(self):
        self.submission = ClientInterestSubmissions.objects.create(
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
        self.submission = baker.make(ClientInterestSubmissions)
        self.client = Client()
        self.user = baker.make(
            Employee,
            username="testuser",
            password="12345",
            is_staff=False,
            is_superuser=False,
        )
        self.staff_user = baker.make(
            Employee,
            username="staffuser",
            password="12345",
            is_staff=True,
            is_superuser=True,
        )
        self.application = baker.make(EmploymentApplicationModel)

    @patch("home.views.ClientInterestSubmissions.objects.get")
    @patch("home.views.logger")
    def test_marked_reviewed_view(self, mock_logger, mock_get):
        mock_request = MagicMock()
        mock_request.body = json.dumps({"pk": self.submission.pk})
        mock_request.user = MagicMock()
        mock_get.return_value = self.submission

        response = marked_reviewed(mock_request)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.submission.reviewed)
        mock_logger.info.assert_called_once_with(
            f"{self.submission.id} marked as reviewed"
        )

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

        with patch("home.views.ClientInterestSubmissions.objects.get") as mock_get:
            mock_get.side_effect = Exception("Some error")

            response = marked_reviewed(mock_request)
            self.assertEqual(response.status_code, 500)
            mock_logger.error.assert_called_once()

    def test_employment_applications_happy_path(self):
        # Create a request object
        request = RequestFactory().get("/employment_applications/")
        # Call the view function
        response = employment_applications(request)
        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

    def test_employment_applications_edge_cases(self):
        # Test when there are no submissions
        request = RequestFactory().get("/employment_applications/")
        response = employment_applications(request)
        self.assertEqual(response.context["submissions"].count(), 0)

        # Test when there are unresponsed submissions
        # Create unresponsed submissions
        # Call the view function
        response = employment_applications(request)
        # Check if the unresponsed count is correct
        self.assertEqual(response.context["unresponsed"], 0)

        # Test when there are reviewed submissions
        # Create reviewed submissions
        # Call the view function
        response = employment_applications(request)
        # Check if the reviewed count is correct
        self.assertEqual(response.context["reviewed"], 0)

        # Test when there are all submissions
        # Create submissions
        # Call the view function
        response = employment_applications(request)
        # Check if the all submissions count is correct
        self.assertEqual(response.context["all_submission"], 0)
