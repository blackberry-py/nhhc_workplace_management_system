from django.test import TestCase
from web.forms import ClientInterestForm, EmploymentApplicationForm


class TestForms(TestCase):
    def test_client_interest_form(self):
        test_cases = [
            # Happy path
            (
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "contact_number": "+17082286900",
                    "email": "john.doe@example.com",
                    "home_address1": "123 Main St",
                    "home_address2": "Apt 4",
                    "city": "Anytown",
                    "state": "CA",
                    "zipcode": "12345",
                    "insurance_carrier": "Carrier",
                    "desired_service": "Service",
                    "captcha": "PASSED",
                },
                True,
                {},
            ),
            # Missing required fields
            (
                {
                    "first_name": "",
                    "last_name": "",
                    "contact_number": "",
                    "email": "",
                    "home_address1": "",
                    "home_address2": "",
                    "city": "",
                    "state": "",
                    "zipcode": "",
                    "insurance_carrier": "",
                    "desired_service": "",
                    "captcha": "",
                },
                False,
                {
                    "first_name": ["This field is required."],
                    "last_name": ["This field is required."],
                    "contact_number": ["This field is required."],
                    "email": ["This field is required."],
                    "home_address1": ["This field is required."],
                    "city": ["This field is required."],
                    "state": ["This field is required."],
                    "zipcode": ["This field is required."],
                    "insurance_carrier": ["This field is required."],
                    "desired_service": ["This field is required."],
                    "captcha": ["This field is required."],
                },
            ),
            # Invalid email format
            (
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "contact_number": "+17082286900",
                    "email": "invalid-email",
                    "home_address1": "123 Main St",
                    "home_address2": "Apt 4",
                    "city": "Anytown",
                    "state": "CA",
                    "zipcode": "12345",
                    "insurance_carrier": "Carrier",
                    "desired_service": "Service",
                    "captcha": "PASSED",
                },
                False,
                {"email": ["Enter a valid email address."]},
            ),
        ]

        for data, expected_valid, expected_errors in test_cases:
            with self.subTest(data=data):
                form = ClientInterestForm(data=data)
                self.assertEqual(form.is_valid(), expected_valid)
                self.assertEqual(form.errors, expected_errors)

    def test_employment_application_form(self):
        test_cases = [
            # Happy path
            (
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "contact_number": "+17082286900",
                    "email": "jane.doe@example.com",
                    "home_address1": "456 Main St",
                    "home_address2": "Apt 5",
                    "city": "Othertown",
                    "state": "NY",
                    "zipcode": "54321",
                    "mobility": "Yes",
                    "ipdh_registered": True,
                    "prior_experience": "5 years",
                    "availability_monday": True,
                    "availability_tuesday": False,
                    "availability_wednesday": False,
                    "availability_thursday": False,
                    "availability_friday": False,
                    "availability_saturday": False,
                    "availability_sunday": False,
                    "resume_cv": None,
                    "captcha": "PASSED",
                },
                True,
                {},
            ),
            # Missing required fields
            (
                {
                    "first_name": "",
                    "last_name": "",
                    "contact_number": "",
                    "email": "",
                    "home_address1": "",
                    "home_address2": "",
                    "city": "",
                    "state": "",
                    "zipcode": "",
                    "mobility": "",
                    "ipdh_registered": "",
                    "prior_experience": "",
                    "availability_monday": False,
                    "availability_tuesday": False,
                    "availability_wednesday": False,
                    "availability_thursday": False,
                    "availability_friday": False,
                    "availability_saturday": False,
                    "availability_sunday": False,
                    "resume_cv": None,
                    "captcha": "",
                },
                False,
                {
                    "first_name": ["This field is required."],
                    "last_name": ["This field is required."],
                    "contact_number": ["This field is required."],
                    "email": ["This field is required."],
                    "home_address1": ["This field is required."],
                    "city": ["This field is required."],
                    "state": ["This field is required."],
                    "zipcode": ["This field is required."],
                    "mobility": ["This field is required."],
                    "prior_experience": ["This field is required."],
                    "captcha": ["This field is required."],
                    "__all__": ["You Must be Available at least 1 day a week. Please review the Work Availability Section"],
                },
            ),
            # Invalid email format
            (
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "contact_number": "+17082286900",
                    "email": "invalid-email",
                    "home_address1": "456 Main St",
                    "home_address2": "Apt 5",
                    "city": "Othertown",
                    "state": "NY",
                    "zipcode": "54321",
                    "mobility": "Yes",
                    "ipdh_registered": True,
                    "prior_experience": "5 years",
                    "availability_monday": True,
                    "availability_tuesday": False,
                    "availability_wednesday": False,
                    "availability_thursday": False,
                    "availability_friday": False,
                    "availability_saturday": False,
                    "availability_sunday": False,
                    "resume_cv": None,
                    "captcha": "PASSED",
                },
                False,
                {"email": ["Enter a valid email address."]},
            ),
        ]

        for data, expected_valid, expected_errors in test_cases:
            with self.subTest(data=data):
                form = EmploymentApplicationForm(data=data)
                self.assertEqual(form.is_valid(), expected_valid)
                self.assertEqual(form.errors, expected_errors)
