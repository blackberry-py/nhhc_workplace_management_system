import pytest
from django.urls import reverse
from django.test import RequestFactory, TestCase
from django.http import HttpRequest
from web.views import HomePageView, AboutUsView, SuccessfulSubmission, ClientInterestFormView, EmploymentApplicationFormView, favicon
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from unittest.mock import patch, MagicMock

@pytest.mark.django_db
class TestViews(TestCase):
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def mock_google_maps_api_key(self, monkeypatch):
        monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'fake-api-key')

    @pytest.mark.parametrize("view_class, template_name, extra_context", [
        (HomePageView, "index.html", {"title": "Home"}),
        (AboutUsView, "about.html", {"title": "About Nett Hands"}),
        (SuccessfulSubmission, "submission.html", {"title": "Submission Successful"}),
    ], ids=["HomePageView", "AboutUsView", "SuccessfulSubmission"])
    def test_public_views_get(self, request_factory, view_class, template_name, extra_context):
        # Arrange
        request = request_factory.get(reverse(view_class.__name__.lower()))

        # Act
        response = view_class.as_view()(request)

        # Assert
        assert response.status_code == 200
        assert template_name in response.template_name
        assert response.context_data['extra_context'] == extra_context

    @pytest.mark.parametrize("form_data, expected_status_code", [
        ({"contact_number": "1234567890"}, 302),
        ({}, 200),
    ], ids=["valid_form", "invalid_form"])
    def test_client_interest_form_view_post(self, request_factory, mock_google_maps_api_key, form_data, expected_status_code):
        # Arrange
        request = request_factory.post(reverse('client_interest'), data=form_data)
        view = ClientInterestFormView()

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize("form_data, expected_status_code", [
        ({"contact_number": "1234567890"}, 302),
        ({}, 200),
    ], ids=["valid_form", "invalid_form"])
    def test_employment_application_form_view_post(self, request_factory, mock_google_maps_api_key, form_data, expected_status_code):
        # Arrange
        request = request_factory.post(reverse('application'), data=form_data)
        view = EmploymentApplicationFormView()

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == expected_status_code

    def test_favicon(self, request_factory):
        # Arrange
        request = request_factory.get(reverse('favicon'))

        # Act
        response = favicon(request)

        # Assert
        assert response.status_code == 200
        assert response['Content-Type'] == 'image/x-icon'

    @patch('web.views.process_new_application')
    def test_client_interest_form_view_process_submitted_client_interest(self, mock_process_new_application, request_factory, mock_google_maps_api_key):
        # Arrange
        form_data = {"contact_number": "1234567890"}
        form = ClientInterestForm(data=form_data)
        form.is_valid()
        view = ClientInterestFormView()

        # Act
        response = view.process_submitted_client_interest(form)

        # Assert
        assert response.status_code == 302
        mock_process_new_application.assert_called_once()

    @patch('web.views.process_new_application')
    def test_employment_application_form_view_process_submitted_application(self, mock_process_new_application, request_factory, mock_google_maps_api_key):
        # Arrange
        form_data = {"contact_number": "1234567890"}
        form = EmploymentApplicationForm(data=form_data)
        form.is_valid()
        view = EmploymentApplicationFormView()

        # Act
        response = view.process_submitted_application(form)

        # Assert
        assert response.status_code == 302
        mock_process_new_application.assert_called_once()
