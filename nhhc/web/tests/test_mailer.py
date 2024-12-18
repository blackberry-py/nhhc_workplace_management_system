# from django.conf import settings
# from django.core import mail
# from django.test import TestCase
# from employee.models import Employee
# from employee.views import Hire
# from model_bakery import baker
# from web.forms import EmploymentApplicationForm

# from nhhc.utils.mailer import PostOffice
# from nhhc.utils.testing import (
#     generate_random_encrypted_char,
#     generate_random_encrypted_email,
# )

# baker.generators.add("sage_encrypt.fields.asymmetric.EncryptedCharField", generate_random_encrypted_char)
# baker.generators.add("sage_encrypt.fields.asymmetric.EncryptedEmailField", generate_random_encrypted_email)


# class TestPostOffice(TestCase):
#     def setUp(self) -> None:
#         self.post_office = PostOffice("Tests@netthandshome.care")
#         self.recipient = settings.ADMINS
#         self.hired_applicant = baker.make(EmploymentApplicationForm, email="Terry@BrooksJr.com")
#         self.rejected_applicant = baker.make(EmploymentApplicationForm, email="Terry@BrooksJr.com")
#         self.terminated_employee = baker.make(Employee, email="Terry@BrooksJr.com")
#         return super().setUp()

#     def test_send_email(self):
#         self.post_office.send_external_application_submission_confirmation(self.hired_applicant)
#         mail.send_mail("Subject here", "Here is the message.", "from@example.com", ["to@example.com"], fail_silently=False)
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(mail.outbox[0].subject, "Subject here")
