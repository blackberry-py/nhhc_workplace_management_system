from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from employee.views import employee_details, hire, reject, send_new_user_credentials
from model_bakery import baker
from web.models import EmploymentApplicationModel


class TestEmployeeActions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = baker.make(get_user_model(), username="testuser", password="12345")
        self.accepted_applicant = baker.make(EmploymentApplicationModel, pk=1)
        self.rejected_applicant = baker.make(EmploymentApplicationModel, pk=2)

    def test_hire_employee(self):
        request = self.factory.post("/hire/", {"pk": 1})
        request.user = self.user
        response = hire(request)
        self.assertEqual(response.status_code, 201)

    def test_reject_employee(self):
        request.user = self.user
        request = self.factory.post("/reject/", {"pk": 2})
        response = reject(request)
        self.assertEqual(response.status_code, 204)

    @patch("myapp.views.send_mail")
    def test_send_new_user_credentials(self, mock_send_mail):
        new_user = User.objects.create_user(
            username="newuser", password="12345", email="newuser@example.com"
        )
        send_new_user_credentials(new_user)
        mock_send_mail.assert_called_once()

    def test_employee_details_permission_denied(self):
        request = self.factory.get("/employee/1/")
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            employee_details(request, 1)

    def test_employee_details_staff_user(self):
        staff_user = User.objects.create_user(
            username="staffuser", password="12345", is_staff=True
        )
        request = self.factory.get("/employee/1/")
        request.user = staff_user
        response = employee_details(request, 1)
        self.assertEqual(response.status_code, 200)
