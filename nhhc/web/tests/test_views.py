import json
from http import HTTPStatus
from unittest.mock import patch

from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from faker import Faker
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from web.views import ClientInterestFormView, EmploymentApplicationFormView, favicon, HomePageView, AboutUsView,SuccessfulSubmission
from django.urls import reverse

test_data = Faker()


class TestStaticViews(TestCase):
    def test_home_page(self):
        request = RequestFactory().get(reverse('web:home'))
        view = HomePageView()
        view.setup(request)
        response = HomePageView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_about_us_page(self):
        request = RequestFactory().get(reverse('web:about_us'))
        view = AboutUsView()
        view.setup(request)
        response = AboutUsView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_successful_submission_page(self):
        request = RequestFactory().get(reverse('web:form_submission_success'))
        view = SuccessfulSubmission()
        view.setup(request)
        response = SuccessfulSubmission.as_view()(request)
        self.assertEqual(response.status_code, 200)
        

    def test_homepage_url(self):
        assert reverse("web:home") == "/"

    def test_about_url(self):
        assert reverse("web:about_us") == "/about/"


class RobotsTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self. client.get("/robots.txt")
        self.assertEqual(302, response.status_code)

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")
        self.assertEqual(302, response.status_code)

