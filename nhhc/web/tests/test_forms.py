from django.test import RequestFactory, TestCase
from django.urls import reverse
from web.forms import ClientInterestForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from web.views import ClientInterestFormView, EmploymentApplicationFormView

from nhhc.utils.testing import generate_mock_ZipCodeField

mock_zipcode = generate_mock_ZipCodeField()


class TestFields(TestCase):

    def test_client_success_response(self): ...


class TestApplicationFormView(TestCase):

    def test_create_application_client(self):
        # Verify the form loads:
        r = self.client.get(reverse("web:employment_application_form"))
        self.assertEqual(r.status_code, 200)

    def test_create_application_form_submit_client(self):

        # Fill out the form and submit it:
        data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "TERRY@BROOKSJR.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": mock_zipcode,
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": True,
            "availability_monday": True,
            "availability_tuesday": False,
            "availability_wednesday": True,
            "availability_thursday": True,
            "availability_friday": True,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        r = self.client.post(reverse("web:employment_application_form"), data=data)
        self.assertEqual(r.status_code, 302)

        # Verify the new fruit was created:
        application = EmploymentApplicationModel.objects.get(first_name=data.get("first_name"))
        self.assertEqual(str(application.state), str(data.get("state")))
        self.assertEqual(application.email, data.get("email"))

    def test_create_application_form(self):
        """
        Verify the form loads
        """
        # Verify the form loads:
        request = RequestFactory().get(reverse("web:employment_application_form"))
        view = EmploymentApplicationFormView()
        view.setup(request)
        response = EmploymentApplicationFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Verify the fields are on the form:
        form = view.get_form()
        self.assertIn("email", form.fields.keys())
        self.assertIn("contact_number", form.fields.keys())
        self.assertIn("first_name", form.fields.keys())
        self.assertIn("last_name", form.fields.keys())

    def test_create_application_submit_invalid(self):
        """
        Verify the record is not created if invalid values are passed to the form:
        """

        # Fill out the form and submit it:
        data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "944",
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": False,
            "availability_monday": False,
            "availability_tuesday": False,
            "availability_wednesday": False,
            "availability_thursday": False,
            "availability_friday": False,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        request = RequestFactory().post(reverse("web:employment_application_form"), data=data)

        view = EmploymentApplicationFormView()
        view.setup(request)

        # Verify the form returned errors:
        form = view.get_form()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(field="availability_monday"))
        self.assertTrue(form.has_error(field="zipcode"))

        # Verify the new fruit was not created:
        self.assertFalse(EmploymentApplicationModel.objects.filter(home_address1=data.get("home_address1")).exists())


class TestClientServiceRequestFormView(TestCase):

    def test_create_client_service_request_client(self):
        # Verify the form loads:
        r = self.client.get(reverse("web:client_interest_form"))
        self.assertEqual(r.status_code, 200)

    def test_create_client_service_request_form_submit_client(self):

        # Fill out the form and submit it:
        data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "insurance_carrier": "BCBS",
            "desired_service": "OT",
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        r = self.client.post(reverse("web:client_interest_form"), data=data)
        self.assertEqual(r.status_code, 301)

        # Verify the new fruit was created:
        application = ClientInterestSubmission.objects.get(email=data.get("email"))
        self.assertEqual(str(application.state), str(data.get("state")))
        self.assertEqual(application.email, data.get("email"))

    def test_create_client_service_request_form(self):
        """
        Verify the form loads with the correct data
        """
        # Verify the form loads:
        request = RequestFactory().get(reverse("web:client_interest_form"))
        view = ClientInterestFormView()
        view.setup(request)
        response = ClientInterestFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Verify the fields are on the form:
        form = view.get_form()
        self.assertIn("email", form.fields.keys())
        self.assertIn("contact_number", form.fields.keys())
        self.assertIn("first_name", form.fields.keys())
        self.assertIn("last_name", form.fields.keys())

    def test_create_client_service_request_submit_invalid(self):
        """
        Verify the record is not created if invalid values are passed to the form:
        """

        # Fill out the form and submit it:
        data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "944",
            "insurance_carrier": "BCBS",
            "desired_service": True,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        request = RequestFactory().post(reverse("web:client_interest_form"), data=data)

        view = ClientInterestFormView()
        view.setup(request)

        # Verify the form returned errors:
        form = view.get_form()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(field="desired_service"))
        self.assertTrue(form.has_error(field="zipcode"))

        # Verify the new fruit was not created:
        self.assertFalse(ClientInterestSubmission.objects.filter(home_address1=data.get("home_address1")).exists())
