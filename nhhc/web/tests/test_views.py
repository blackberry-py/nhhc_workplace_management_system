import json
from http import HTTPStatus

from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from faker import Faker
from web.views import ClientInterestFormView, EmploymentApplicationFormView, favicon

test_data = Faker()


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_client_interest_form_view_get(self):
        request = self.factory.get("/client-interest/")
        response = ClientInterestFormView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_employment_application_form_view_get(self):
        request = self.factory.get("/employment-application/")
        response = EmploymentApplicationFormView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_favicon_view_get(self):
        request = self.factory.get("/favicon.ico")
        response = favicon(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_client_interest_form_view_post_invalid(self):
        request = self.factory.post(
            "/client-interest/",
            data={
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
                "desired_service": False,
            },
        )
        response = ClientInterestFormView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_employment_application_form_view_post_invalid(self):
    #     request = self.factory.post('/employment-application/', data={})
    #     response = EmploymentApplicationFormView.as_view()(request)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_client_interest_form_view_post_valid(self):
        data = {
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
            "desired_service": "OT",
        }
        request = self.factory.post("/client-interest/", data=data)
        response = ClientInterestFormView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_employment_application_form_view_post_valid(self):
        data = {
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
        request = self.factory.post("/employment-application/", data=data)
        response = EmploymentApplicationFormView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class RobotsTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)
