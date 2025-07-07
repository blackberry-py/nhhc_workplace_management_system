from django.test import TestCase
from employee.models import Employee
from faker import Faker
from model_bakery import baker
from nhhc.utils.testing import (
    generate_mock_PhoneNumberField,
    generate_mock_ZipCodeField,
)
from web.models import EmploymentApplicationModel

dummy = Faker()


class TestEmploymentApplicationModel(TestCase):
    def test_hire_applicant(self):
        mock_number = generate_mock_PhoneNumberField()
        mock_zipcode = generate_mock_ZipCodeField()
        new_employee = baker.make(
            EmploymentApplicationModel,
            last_name="test",
            first_name="new_employee",
            contact_number=mock_number,
            email="testing_email@netthandshome.care",
            home_address1="1 North World Trade Tower",
            home_address2="15th Floor",
            city="Manhattan",
            state="NY",
            zipcode=mock_zipcode,
            mobility="C",
            prior_experience="J",
            ipdh_registered=True,
            availability_monday=True,
            availability_tuesday=False,
            availability_wednesday=True,
            availability_thursday=True,
            availability_friday=True,
            availability_saturday=False,
        )
        hiring_manager = baker.make(Employee)
        new_employee.hire_applicant(hired_by=hiring_manager)

        self.assertTrue(new_employee.reviewed)
        self.assertTrue(new_employee.hired)
        self.assertEqual(new_employee.reviewed_by, hiring_manager)

    # def test_reject_applicant(self):
    #     rejected_applicant = baker.make(
    #         EmploymentApplicationModel,
    #         last_name="test",
    #         first_name="rejected_applicant",
    #     )
    #     hiring_manager = baker.make(Employee)
    #     rejected_applicant.reject_applicant(rejected_by=hiring_manager)

    #     self.assertTrue(rejected_applicant.reviewed)
    #     self.assertFalse(rejected_applicant.hired)
    #     self.assertEqual(rejected_applicant.reviewed_by, hiring_manager)
