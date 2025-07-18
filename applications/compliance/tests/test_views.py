from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.test import TestCase

from applications.employee.models import Employee
from applications.employee.views import Hire


class TestEmployeeViews(TestCase):
    def test_hire_success(self):
        request = HttpRequest()
        request.method = "POST"
        # Mock a superuser
        mock_user = MagicMock(spec=Employee)
        mock_user.is_authenticated = True
        mock_user.is_superuser = True
        request.user = mock_user
        request.POST = {"pk": 1}

        with (
            patch("applications.employee.views.EmploymentApplicationModel.objects.get") as mock_get,
            patch("applications.employee.views.send_async_onboarding_email.delay") as mock_send_async_onboarding_email,
        ):
            mock_applicant = MagicMock()
            mock_get.return_value = mock_applicant
            mock_applicant.hire_applicant.return_value = {"email": "test@example.com", "first_name": "John", "plain_text_password": "password", "username": "john_doe", "employee_id": 123}

            response = Hire.hire(request)

            self.assertEqual(response.status_code, 201)
            self.assertIn(b"username: john_doe,  password: password, employee_id: 123", response.content)
            mock_applicant.save.assert_called()
            mock_applicant.hire_applicant.assert_called_with(hired_by=request.user)
            mock_applicant.save.assert_called()
            mock_send_async_onboarding_email.assert_called_with({"new_user_email": "test@example.com", "new_user_first_name": "John", "plaintext_temp_password": "password", "username": "john_doe"})

    def test_hire_unauthorized(self):
        request = HttpRequest()
        request.method = "POST"
        # Use anonymous user (not authenticated)
        request.user = AnonymousUser()

        response = Hire.hire(request)

        self.assertEqual(response.status_code, 403)

    def test_hire_invalid_pk(self):
        request = HttpRequest()
        request.method = "POST"
        # Mock a superuser
        mock_user = MagicMock(spec=Employee)
        mock_user.is_authenticated = True
        mock_user.is_superuser = True
        request.user = mock_user
        request.POST = {"pk": "invalid"}

        response = Hire.hire(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Failed to hire applicant. Invalid or no 'pk' value provided", response.content)

    # Add more test cases for reject, terminate, and promote functions
