from django.urls import reverse
from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from web.views import HomePageView, AboutUsView, SuccessfulSubmission, ClientInterestFormView, EmploymentApplicationFormView, favicon
from web.forms import ClientInterestForm, EmploymentApplicationForm


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.fake_api_key = "fake-api-key"

    def setUp(self):
        self.factory = RequestFactory()

    def test_public_views_get(self):
        views = [
            (HomePageView, "index.html", {"title": "Home"}),
            (AboutUsView, "about.html", {"title": "About Nett Hands"}),
            (SuccessfulSubmission, "submission.html", {"title": "Submission Successful"}),
        ]

        for view_class, template_name, extra_context in views:
            with self.subTest(view=view_class):
                request = self.factory.get(reverse(view_class.__name__.lower()))
                response = view_class.as_view()(request)

                self.assertEqual(response.status_code, 200)
                self.assertIn(template_name, response.template_name)
                self.assertEqual(response.context_data["extra_context"], extra_context)

    def test_client_interest_form_view_post(self):
        form_data_cases = [({"contact_number": "1234567890"}, 302), ({}, 200)]  # Valid form  # Invalid form

        for form_data, expected_status_code in form_data_cases:
            with self.subTest(form_data=form_data):
                request = self.factory.post(reverse("client_interest"), data=form_data)
                response = ClientInterestFormView.as_view()(request)

                self.assertEqual(response.status_code, expected_status_code)

    def test_employment_application_form_view_post(self):
        form_data_cases = [({"contact_number": "1234567890"}, 302), ({}, 200)]  # Valid form  # Invalid form

        for form_data, expected_status_code in form_data_cases:
            with self.subTest(form_data=form_data):
                request = self.factory.post(reverse("application"), data=form_data)
                response = EmploymentApplicationFormView.as_view()(request)

                self.assertEqual(response.status_code, expected_status_code)

    def test_favicon(self):
        request = self.factory.get(reverse("favicon"))
        response = favicon(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/x-icon")

    @patch("web.views.process_new_application")
    def test_client_interest_form_view_process_submitted_client_interest(self, mock_process_new_application):
        form_data = {"contact_number": "1234567890"}
        form = ClientInterestForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = ClientInterestFormView().process_submitted_client_interest(form)

        self.assertEqual(response.status_code, 302)
        mock_process_new_application.assert_called_once()

    @patch("web.views.process_new_application")
    def test_employment_application_form_view_process_submitted_application(self, mock_process_new_application):
        form_data = {"contact_number": "1234567890"}
        form = EmploymentApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = EmploymentApplicationFormView().process_submitted_application(form)

        self.assertEqual(response.status_code, 302)
        mock_process_new_application.assert_called_once()
