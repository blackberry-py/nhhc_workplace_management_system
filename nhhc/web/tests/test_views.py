import json
from http import HTTPStatus
from unittest.mock import patch

from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from faker import Faker

from web.views import ClientInterestFormView, EmploymentApplicationFormView, favicon
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel

test_data = Faker()


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def _assert_get_request_returns_ok(self, url, view_class):
        """Helper to assert that a GET request to a given view returns HTTP 200 OK."""
        request = self.factory.get(url)
        response = view_class.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def _assert_post_request_returns_ok(self, url, view_class, data):
        """Helper to assert that a POST request to a given view returns HTTP 200 OK."""
        request = self.factory.post(url, data=data)
        response = view_class.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_client_interest_form_view_get(self):
        # If there is a named URL pattern, e.g. 'client_interest', you could do:
        # url = reverse('client_interest')
        # Otherwise, leave as is:
        url = "/client-interest/"
        self._assert_get_request_returns_ok(url, ClientInterestFormView)

    def test_employment_application_form_view_get(self):
        # If there is a named URL pattern, e.g. 'employment_application', you could do:
        # url = reverse('employment_application')
        # Otherwise, leave as is:
        url = "/employment-application/"
        self._assert_get_request_returns_ok(url, EmploymentApplicationFormView)

    def test_favicon_view_get(self):
        request = self.factory.get("/favicon.ico")
        response = favicon(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_client_interest_form_view_post_invalid(self):
        invalid_data = {
            "last_name": "test",
            "first_name": "client",
            "contact_number": "+17087996100",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "insurance_carrier": "TEST INSURANCE",
            "desired_service": False,  # Invalid because we expected a string like 'OT' or missing required data
        }
        form = ClientInterestForm(invalid_data)
        self.assertFalse(form.is_valid())

    def test_client_interest_form_view_post_valid(self):
        valid_data = {
            "last_name": "test",
            "first_name": "client",
            "contact_number": "+17087996100",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "insurance_carrier": "TEST INSURANCE",
            "desired_service": "OT",  # Valid desired service\
        }
        form = ClientInterestForm(valid_data)
        self.assertTrue(form.is_valid())

    def test_employment_application_form_view_post_valid(self):
        valid_data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+17087996100",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": "True",
            "availability_monday": True,
            "availability_tuesday": False,
            "availability_wednesday": True,
            "availability_thursday": True,
            "availability_friday": True,
            "availability_saturday": False,
        }
        form= EmploymentApplicationForm(valid_data)
        self.assetTrue(form.is_valid())


    def test_employment_application_form_view_post_invalid(self):
        valid_data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+17087996100",
            "email": "Dev@gmail.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": "True",
            "availability_monday": False,
            "availability_tuesday": False,
            "availability_wednesday": False,
            "availability_thursday": False,
            "availability_friday": False,
            "availability_saturday": False,
        }
        form= EmploymentApplicationForm(valid_data)
        self.assetFalse(form.is_valid())
    


class RobotsTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(HTTPStatus.TEMPORARY_REDIRECT, response.status_code)

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)