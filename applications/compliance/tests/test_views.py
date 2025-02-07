from unittest.mock import MagicMock, patch

from django.http import HttpRequest
from django.test import TestCase
from employee.views import hire


class TestEmployeeViews(TestCase):
    def test_hire_success(self):
        request = HttpRequest()
        request.user.is_authenticated = True
        request.user.is_superuser = True
        request.POST = {"pk": 1}

        with patch("employee.views.EmploymentApplicationModel.objects.get") as mock_get:
            mock_applicant = MagicMock()
            mock_get.return_value = mock_applicant
            mock_applicant.hire_applicant.return_value = {"email": "test@example.com", "first_name": "John", "plain_text_password": "password", "username": "john_doe", "employee_id": 123}

            response = hire(request)

            self.assertEqual(response.status_code, 201)
            self.assertIn(b"username: john_doe,  password: password, employee_id: 123", response.content)
            mock_applicant.save.assert_called()
            mock_applicant.hire_applicant.assert_called_with(hired_by=request.user)
            mock_applicant.save.assert_called()
            mock_send_async_onboarding_email = mock_send_async_onboarding_email.delay
            mock_send_async_onboarding_email.assert_called_with({"new_user_email": "test@example.com", "new_user_first_name": "John", "plaintext_temp_password": "password", "username": "john_doe"})

    def test_hire_unauthorized(self):
        request = HttpRequest()
        request.user.is_authenticated = False
        request.user.is_superuser = False

        response = hire(request)

        self.assertEqual(response.status_code, 403)

    def test_hire_invalid_pk(self):
        request = HttpRequest()
        request.user.is_authenticated = True
        request.user.is_superuser = True
        request.POST = {"pk": "invalid"}

        response = hire(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Failed to hire applicant. Invalid or no 'pk' value provided in the request.", response.content)

    # Add more test cases for reject, terminate, and promote functions
