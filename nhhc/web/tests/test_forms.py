from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponsePermanentRedirect
from django.test import TestCase
from django.urls import reverse
from web.forms import ClientInterestForm
from web.views import form_valid


@pytest.mark.parametrize(
    "form_data, expected_redirect, expected_log_message, expected_task_call, test_id",
    [
        (
            {"name": "John Doe", "email": "john@example.com"},
            reverse("submitted"),
            "Form Is Valid",
            True,
            "valid_form_submission",
        ),
        (
            {"name": "", "email": "invalid-email"},
            reverse("client_interest"),
            "Form Is Invalid",
            False,
            "invalid_form_submission",
        ),
    ],
    ids=lambda x: x[-1],
)
@patch("web.views.process_new_client_interest")
@patch("web.views.logger")
class TestFormSubmissions(TestCase):
    def test_form_valid(self, mock_logger, mock_process_new_client_interest, form_data, expected_redirect, expected_log_message, expected_task_call, test_id):
        # Arrange
        form = ClientInterestForm(data=form_data)
        view_instance = MagicMock()
        view_instance.form_valid = form_valid

        # Act
        response = view_instance.form_valid(form)

        # Assert
        assert isinstance(response, HttpResponsePermanentRedirect)
        assert response.url == expected_redirect
        mock_logger.debug.assert_called_with(expected_log_message)
        # sourcery skip: no-conditionals-in-tests
        if expected_task_call:
            mock_process_new_client_interest.assert_called_once_with(form.cleaned_data)
        else:
            mock_process_new_client_interest.assert_not_called()
