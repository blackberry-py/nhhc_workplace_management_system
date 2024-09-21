from datetime import datetime
from django.test import TestCase
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from employee.models import Employee


class TestClientInterestSubmission(TestCase):
    def test_client_interest_submission_str(self):
        test_cases = [
            # Test cases
            ("John", "Doe", "john.doe@example.com", "+1234567890", "123 Main St", "Apt 4", "Springfield", "12345", "IL", "Carrier A", "I", False, None, "Doe, John - Submission Date: 2023-01-01"),
            ("Jane", "Smith", "jane.smith@example.com", "+0987654321", "456 Elm St", "", "Shelbyville", "54321", "CA", "Carrier B", "NM", True, 1, "Smith, Jane - Submission Date: 2023-01-01"),
        ]

        for first_name, last_name, email, contact_number, home_address1, home_address2, city, zipcode, state, insurance_carrier, desired_service, reviewed, reviewed_by, expected_str in test_cases:
            with self.subTest(first_name=first_name, last_name=last_name):
                # Arrange
                submission = ClientInterestSubmission(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    contact_number=contact_number,
                    home_address1=home_address1,
                    home_address2=home_address2,
                    city=city,
                    zipcode=zipcode,
                    state=state,
                    insurance_carrier=insurance_carrier,
                    desired_service=desired_service,
                    reviewed=reviewed,
                    reviewed_by=reviewed_by,
                    date_submitted=datetime(2023, 1, 1),
                )

                # Act
                result = str(submission)

                # Assert
                self.assertEqual(result, expected_str)

    def test_marked_reviewed(self):
        # Arrange
        employee = Employee.objects.create(first_name="Reviewer", last_name="One")
        submission = ClientInterestSubmission(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            contact_number="+1234567890",
            home_address1="123 Main St",
            home_address2="Apt 4",
            city="Springfield",
            zipcode="12345",
            state="IL",
            insurance_carrier="Carrier A",
            desired_service="I",
            reviewed=False,
            reviewed_by=None,
            date_submitted=datetime(2023, 1, 1),
        )
        submission.save()

        # Act
        submission.marked_reviewed(employee)

        # Assert
        self.assertTrue(submission.reviewed)
        self.assertEqual(submission.reviewed_by, employee)


class TestEmploymentApplicationModel(TestCase):
    def test_employment_application_model_str(self):
        test_cases = [
            # Test cases
            (
                "John",
                "Doe",
                "+1234567890",
                "john.doe@example.com",
                "123 Main St",
                "Apt 4",
                "Springfield",
                "IL",
                "12345",
                "C",
                "S",
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                None,
                "Doe, John (1) - Submission Date: 2023-01-01",
            ),
            (
                "Jane",
                "Smith",
                "+0987654321",
                "jane.smith@example.com",
                "456 Elm St",
                "",
                "Shelbyville",
                "CA",
                "54321",
                "P",
                "J",
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                1,
                "Smith, Jane (2) - Submission Date: 2023-01-01",
            ),
        ]

        for (
            first_name,
            last_name,
            contact_number,
            email,
            home_address1,
            home_address2,
            city,
            state,
            zipcode,
            mobility,
            prior_experience,
            ipdh_registered,
            availability_monday,
            availability_tuesday,
            availability_wednesday,
            availability_thursday,
            availability_friday,
            availability_saturday,
            availability_sunday,
            reviewed,
            hired,
            reviewed_by,
            expected_str,
        ) in test_cases:
            with self.subTest(first_name=first_name, last_name=last_name):
                # Arrange
                application = EmploymentApplicationModel(
                    first_name=first_name,
                    last_name=last_name,
                    contact_number=contact_number,
                    email=email,
                    home_address1=home_address1,
                    home_address2=home_address2,
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    mobility=mobility,
                    prior_experience=prior_experience,
                    ipdh_registered=ipdh_registered,
                    availability_monday=availability_monday,
                    availability_tuesday=availability_tuesday,
                    availability_wednesday=availability_wednesday,
                    availability_thursday=availability_thursday,
                    availability_friday=availability_friday,
                    availability_saturday=availability_saturday,
                    availability_sunday=availability_sunday,
                    reviewed=reviewed,
                    hired=hired,
                    reviewed_by=reviewed_by,
                    date_submitted=datetime(2023, 1, 1),
                )

                # Act
                result = str(application)

                # Assert
                self.assertEqual(result, expected_str)

    def test_hire_applicant(self):
        # Arrange
        employee = Employee.objects.create(first_name="Reviewer", last_name="One")
        application = EmploymentApplicationModel(
            first_name="John",
            last_name="Doe",
            contact_number="+1234567890",
            email="john.doe@example.com",
            home_address1="123 Main St",
            home_address2="Apt 4",
            city="Springfield",
            state="IL",
            zipcode="12345",
            mobility="C",
            prior_experience="S",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=True,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=True,
            availability_sunday=True,
            reviewed=False,
            hired=False,
            reviewed_by=None,
            date_submitted=datetime(2023, 1, 1),
        )
        application.save()

        # Act
        result = application.hire_applicant(employee)

        # Assert
        self.assertTrue(application.hired)
        self.assertTrue(application.reviewed)
        self.assertEqual(application.reviewed_by, employee)
        self.assertIn("user", result)
        self.assertIn("plain_text_password", result)
        self.assertIn("username", result)
        self.assertIn("employee_id", result)
        self.assertIn("email", result)
        self.assertIn("first_name", result)
        self.assertIn("last_name", result)

    def test_reject_applicant(self):
        # Arrange
        employee = Employee.objects.create(first_name="Reviewer", last_name="One")
        application = EmploymentApplicationModel(
            first_name="John",
            last_name="Doe",
            contact_number="+1234567890",
            email="john.doe@example.com",
            home_address1="123 Main St",
            home_address2="Apt 4",
            city="Springfield",
            state="IL",
            zipcode="12345",
            mobility="C",
            prior_experience="S",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=True,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=True,
            availability_sunday=True,
            reviewed=False,
            hired=False,
            reviewed_by=None,
            date_submitted=datetime(2023, 1, 1),
        )
        application.save()

        # Act
        application.reject_applicant(employee)

        # Assert
        self.assertFalse(application.hired)
        self.assertTrue(application.reviewed)
        self.assertEqual(application.reviewed_by, employee)
