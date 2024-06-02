from django.test import TestCase
from django.core import mail
from nhhc.utils.mailer import PostOffice
from web.forms import EmploymentApplicationForm
from model_bakery import baker
from nhhc.utils.testing import generate_random_encrypted_char, generate_random_encrypted_email

baker.generators.add("sage_encrypt.fields.asymmetric.EncryptedCharField", generate_random_encrypted_char)
baker.generators.add("sage_encrypt.fields.asymmetric.EncryptedEmailField", generate_random_encrypted_email)


class TestPostOffice(TestCase):
    def test_send_external_application_submission_confirmation_happy_path(self) -> None:
        inital_values = {
            "first_name": "Test",
            "last_name": "Case",
            "contact_number": "+14439835591",
            "email": "Terry@BrooksJr.com",
            "home_address1": "16643 S. Kedzie",
            "city": "Baltimore",
            "state": "MD",
            "zipcode:": 60411,
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": False,
            "availability_monday": False,
            "availability_tuesday": True,
            "availability_wednesday": False,
            "availability_thursday": False,
            "availability_friday": True,
            "availability_saturday": True,
            "availability_sunday": False,
        }
        form = EmploymentApplicationForm(initial=inital_values)
        if form.is_valid():
            form.save()
            test = PostOffice.send_external_application_submission_confirmation(form)
        else:
            print(form.errors)
            raise RuntimeError(f"{form.errors}")
        # Test that one message has been sent.
        self.assertEqual(test["external"], 1)
