from django.test import TestCase
from unittest.mock import patch
from nhhc.utils.mailer import PostOffice


class TestPostOffice(TestCase):
    def setUp(self):
        self.post_office = PostOffice(from_email="test@example.com")

    def test_send_external_application_submission_confirmation(self):
        test_cases = [
            (
                {"first_name": "John", "email": "john@example.com"},
                "Thanks For Your Employment Interest, John!",
                "HTML content with John",
                "Plain text content with John",
            ),
            (
                {"first_name": "Jane", "email": "jane@example.com"},
                "Thanks For Your Employment Interest, Jane!",
                "HTML content with Jane",
                "Plain text content with Jane",
            ),
        ]

        for applicant, expected_subject, expected_html_content, expected_text_content in test_cases:
            with self.subTest(applicant=applicant):
                with patch("nhhc.utils.mailer.EmailMultiAlternatives.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_external_application_submission_confirmation(applicant)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_text_content)
                    self.assertEqual(msg.alternatives[0][0], expected_html_content)

    def test_send_external_client_submission_confirmation(self):
        test_cases = [
            (
                {"first_name": "Alice", "email": "alice@example.com"},
                "We Are On It, Alice!",
                "HTML content with Alice",
                "Plain text content with Alice",
            ),
            (
                {"first_name": "Bob", "email": "bob@example.com"},
                "We Are On It, Bob!",
                "HTML content with Bob",
                "Plain text content with Bob",
            ),
        ]

        for client, expected_subject, expected_html_content, expected_text_content in test_cases:
            with self.subTest(client=client):
                with patch("nhhc.utils.mailer.EmailMultiAlternatives.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_external_client_submission_confirmation(client)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_text_content)
                    self.assertEqual(msg.alternatives[0][0], expected_html_content)

    def test_send_external_applicant_rejection_email(self):
        test_cases = [
            (
                {"first_name": "Charlie", "email": "charlie@example.com"},
                "Thank You So Much For Considering Nett Hands, Charlie!",
                "HTML content with Charlie",
                "Plain text content with Charlie",
            ),
            (
                {"first_name": "Dana", "email": "dana@example.com"},
                "Thank You So Much For Considering Nett Hands, Dana!",
                "HTML content with Dana",
                "Plain text content with Dana",
            ),
        ]

        for applicant, expected_subject, expected_html_content, expected_text_content in test_cases:
            with self.subTest(applicant=applicant):
                with patch("nhhc.utils.mailer.EmailMultiAlternatives.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_external_applicant_rejection_email(applicant)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_text_content)
                    self.assertEqual(msg.alternatives[0][0], expected_html_content)

    def test_send_external_applicant_termination_email(self):
        test_cases = [
            (
                {"first_name": "Eve", "email": "eve@example.com"},
                "NOTICE: Termination of Employment from Nett Hands Home Care",
                "Plain text content with Eve",
            ),
            (
                {"first_name": "Frank", "email": "frank@example.com"},
                "NOTICE: Termination of Employment from Nett Hands Home Care",
                "Plain text content with Frank",
            ),
        ]

        for employee, expected_subject, expected_text_content in test_cases:
            with self.subTest(employee=employee):
                with patch("nhhc.utils.mailer.EmailMessage.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_external_applicant_termination_email(employee)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_text_content)

    def test_send_external_applicant_new_hire_onboarding_email(self):
        test_cases = [
            (
                {"first_name": "Grace", "email": "grace@example.com", "username": "grace123", "plaintext_temp_password": "password123"},
                "Welcome to Nett Hands, Grace!",
                "HTML content with Grace",
                "Plain text content with Grace",
            ),
            (
                {"first_name": "Hank", "email": "hank@example.com", "username": "hank123", "plaintext_temp_password": "password123"},
                "Welcome to Nett Hands, Hank!",
                "HTML content with Hank",
                "Plain text content with Hank",
            ),
        ]

        for new_hire, expected_subject, expected_html_content, expected_text_content in test_cases:
            with self.subTest(new_hire=new_hire):
                with patch("nhhc.utils.mailer.EmailMultiAlternatives.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_external_applicant_new_hire_onboarding_email(new_hire)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_text_content)
                    self.assertEqual(msg.alternatives[0][0], expected_html_content)

    def test_send_internal_new_applicant_notification(self):
        test_cases = [
            (
                {
                    "first_name": "Ivy",
                    "last_name": "Smith",
                    "email": "ivy@example.com",
                    "contact_number": "1234567890",
                    "home_address": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zipcode": "12345",
                    "mobility": "Yes",
                    "prior_experience": "None",
                    "availability_monday": "Yes",
                    "availability_tuesday": "Yes",
                    "availability_wednesday": "Yes",
                    "availability_thursday": "Yes",
                    "availability_friday": "Yes",
                    "availability_saturday": "No",
                    "availability_sunday": "No",
                },
                "NOTICE: New Application For Employment - Smith, Ivy!",
                "Internal application notification content with Ivy",
            ),
            (
                {
                    "first_name": "Jack",
                    "last_name": "Doe",
                    "email": "jack@example.com",
                    "contact_number": "0987654321",
                    "home_address": "456 Elm St",
                    "city": "Othertown",
                    "state": "NY",
                    "zipcode": "54321",
                    "mobility": "No",
                    "prior_experience": "Some",
                    "availability_monday": "No",
                    "availability_tuesday": "No",
                    "availability_wednesday": "No",
                    "availability_thursday": "No",
                    "availability_friday": "No",
                    "availability_saturday": "Yes",
                    "availability_sunday": "Yes",
                },
                "NOTICE: New Application For Employment - Doe, Jack!",
                "Internal application notification content with Jack",
            ),
        ]

        for applicant, expected_subject, expected_body in test_cases:
            with self.subTest(applicant=applicant):
                with patch("nhhc.utils.mailer.EmailMessage.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_internal_new_applicant_notification(applicant)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_body)

    def test_send_internal_new_client_service_request_notification(self):
        test_cases = [
            (
                {
                    "first_name": "Karen",
                    "last_name": "Johnson",
                    "email": "karen@example.com",
                    "desired_service": "Service A",
                    "contact_number": "1112223333",
                    "zipcode": "67890",
                    "insurance_carrier": "Carrier A",
                },
                "NOTICE: New Client Service Request - Johnson, Karen!",
                "Internal client service request notification content with Karen",
            ),
            (
                {
                    "first_name": "Leo",
                    "last_name": "Brown",
                    "email": "leo@example.com",
                    "desired_service": "Service B",
                    "contact_number": "4445556666",
                    "zipcode": "98765",
                    "insurance_carrier": "Carrier B",
                },
                "NOTICE: New Client Service Request - Brown, Leo!",
                "Internal client service request notification content with Leo",
            ),
        ]

        for client, expected_subject, expected_body in test_cases:
            with self.subTest(client=client):
                with patch("nhhc.utils.mailer.EmailMessage.send", return_value=1) as mock_send:
                    # Act
                    result = self.post_office.send_internal_new_client_service_request_notification(client)

                    # Assert
                    self.assertEqual(result, 1)
                    mock_send.assert_called_once()
                    msg = mock_send.call_args[0][0]
                    self.assertEqual(msg.subject, expected_subject)
                    self.assertEqual(msg.body, expected_body)
