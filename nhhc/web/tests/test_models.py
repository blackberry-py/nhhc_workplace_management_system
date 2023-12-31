import arrow
from django.test import TestCase
from employee.models import Employee
from model_bakery import baker
from web.models import ClientInterestSubmissions, EmploymentApplicationModel


def gen_phone():
    return "+17082286900"


def gen_zip_code():
    return "21217"


baker.generators.add("phonenumber_field.modelfields.PhoneNumberField", gen_phone)
baker.generators.add("localflavor.us.models.USZipCodeField", gen_zip_code)
# baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', gen_func)
# baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', gen_func)


class TestClientInterestSubmissions(TestCase):
    def setup(self):
        pass

    def test__str__(self):
        string_of_class = baker.make(
            ClientInterestSubmissions,
            last_name="Brooks",
            first_name="Test",
            date_submitted=str(arrow.now(tz="local").format("YYYY-MM-DD hh:mm:ss")),
        )
        self.assertEqual(
            string_of_class.__str__(),
            f"Brooks, Test - Submission Date: {str(arrow.now(tz='local').format('YYYY-MM-DD'))}",
        )

    def test_marked_reviewed(self):
        reviewed_submission = baker.make(ClientInterestSubmissions)
        reviewer = baker.make(Employee)
        reviewed_submission.marked_reviewed(user_id=reviewer)
        assert reviewed_submission.reviewed == True
        assert reviewed_submission.reviewed_by is not None


class TestEmploymentApplicationModel(TestCase):
    def test__str__(self):
        string_of_class = baker.make(
            EmploymentApplicationModel,
            id=1,
            last_name="Suite",
            first_name="EmploymentApplicationModel",
            date_submitted=str(arrow.now(tz="local").format("YYYY-MM-DD hh:mm:ss")),
        )
        self.assertEqual(
            string_of_class.__str__(),
            f"Suite, EmploymentApplicationModel (1) - Submission Date: {arrow.now().format('YYYY-MM-DD')}",
        )

    def test_hire_applicant(self):
        new_empoloyee = baker.make(
            EmploymentApplicationModel, last_name="test", first_name="new_empoloyee"
        )
        hiring_manager = baker.make(Employee)
        new_empoloyee.hire_applicant(hired_by=hiring_manager)

        self.assertTrue(new_empoloyee.reviewed)
        self.assertTrue(new_empoloyee.hired)
        self.assertEqual(new_empoloyee.reviewed_by, hiring_manager)

    def test_reject_applicant(self):
        rejected_applicant = baker.make(
            EmploymentApplicationModel,
            last_name="test",
            first_name="rejected_applicant",
        )
        hiring_manager = baker.make(Employee)
        rejected_applicant.reject_applicant(rejected_by=hiring_manager)

        self.assertTrue(rejected_applicant.reviewed)
        self.assertFalse(rejected_applicant.hired)
        self.assertEqual(rejected_applicant.reviewed_by, hiring_manager)
