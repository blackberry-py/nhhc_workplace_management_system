from django.test import TestCase
from django.contrib.auth import get_user_model
from employee.models import Employee

User = get_user_model()


class EmployeeModelTests(TestCase):
    def test_create_unique_username(self):
        """
        Test creating a unique username using the `create_unique_username` method.
        """
        first_name = "John"
        last_name = "Doe"
        username = Employee.create_unique_username(first_name, last_name)
        self.assertEqual(username, "doe.john")

    def test_create_unique_username_with_existing_username(self):
        """
        Test creating a unique username when the initial username is already taken.
        """
        User.objects.create_user(
            username="doe.john",
            password="testpassword",
            first_name="John",
            last_name="Doe",
        )
        username = Employee.create_unique_username("John", "Doe")
        self.assertEqual(username, "doe.john1")

    def test_create_user(self):
        """
        Test creating a new user using the `create_user` method.
        """
        user = Employee.objects.create_user(
            password="testpassword",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        self.assertEqual(user.username, "doe.john")
        self.assertTrue(user.check_password("testpassword"))

    def test_create_superuser(self):
        """
        Test creating a new superuser using the `create_superuser` method.
        """
        user = Employee.objects.create_superuser(
            username="admin",
            password="testpassword",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
        )
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_is_profile_complete(self):
        """
        Test the `is_profile_complete` method.
        """
        user = Employee.objects.create_user(
            password="testpassword",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        user.social_security = "123-45-6789"
        user.gender = Employee.GENDER.MALE
        user.city = "New York"
        user.phone = "+12125551212"
        user.state = "NY"
        user.street_address1 = "123 Main St"
        user.zipcode = "10001"
        user.emergency_contact_relationship = "Friend"
        user.emergency_contact_last_name = "Smith"
        user.emergency_contact_first_name = "Jane"
        user.marital_status = Employee.MARITAL_STATUS.SINGLE
        user.qualifications = Employee.QUALIFICATIONS.BS
        user.save()

        self.assertTrue(user.is_profile_complete())

    def test_terminate_employment(self):
        """
        Test the `terminate_employment` method.
        """
        user = Employee.objects.create_user(
            password="testpassword",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        user.terminate_employment()
        self.assertIsNotNone(user.termination_date)
        self.assertEqual(user.username, "doe.johnX")
        self.assertFalse(user.is_active)
