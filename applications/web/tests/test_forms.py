from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel
from applications.web.views import ClientInterestFormView, EmploymentApplicationFormView
from common.testing import generate_mock_ZipCodeField

mock_zipcode = generate_mock_ZipCodeField()


class TestFields(TestCase):

    def test_client_success_response(self): ...


class TestApplicationFormView(TestCase):

    def test_create_application_client(self):
        # Verify the form loads:
        r = self.client.get(reverse("web:employment_application_form"))
        self.assertEqual(r.status_code, 200)

    def test_create_application_no_resume_submit_valid(self):
        """Tests submitting a valid employment application without a resume.

        This test verifies the successful submission of an employment application form with valid data.
        It checks that the form submission results in a redirect and creates a corresponding application record.

        Args:
            self: Test case instance.

        Raises:
            AssertionError: If the form submission fails or the created application does not match the submitted data.
        """

        # Fill out the form and submit it:
        data = {
            "last_name": "test_with_resume",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "TERRY@BROOKSJR.com",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": mock_zipcode,
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": True,
            "availability_monday": True,
            "availability_tuesday": False,
            "availability_wednesday": True,
            "availability_thursday": True,
            "availability_friday": True,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        r = self.client.post(reverse("web:employment_application_form"), data=data)
        self.assertEqual(r.status_code, 302)

        # Verify the new submission  was created:
        application = EmploymentApplicationModel.objects.get(first_name=data.get("first_name"))
        self.assertEqual(str(application.state), str(data.get("state")))
        self.assertEqual(application.email, data.get("email"))

    def test_create_application_form(self):
        """
        Verifies the employment application form loads correctly and contains expected fields.

        This test ensures that the employment application form view renders successfully and includes
        the required form fields for submission. It checks both the HTTP response status and the
        presence of critical form fields.

        Args:
            self: Test case instance.

        Raises:
            AssertionError: If the form view fails to load or expected fields are missing.
        """
        # Verify the form loads:
        request = RequestFactory().get(reverse("web:employment_application_form"))
        view = EmploymentApplicationFormView()
        view.setup(request)
        response = EmploymentApplicationFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Verify the fields are on the form:
        form = view.get_form()
        self.assertIn("email", form.fields.keys())
        self.assertIn("contact_number", form.fields.keys())
        self.assertIn("first_name", form.fields.keys())
        self.assertIn("last_name", form.fields.keys())

    def test_create_application_no_resume_submit_invalid(self):
        """Tests submission of an invalid employment application form.

        This test verifies the form validation process by submitting an application with invalid data.
        It checks that the form correctly identifies and reports specific validation errors.

        Args:
            self: Test case instance.

        Raises:
            AssertionError: If form validation fails to detect expected errors or if the application
            is incorrectly created with invalid data.
        """
        # Fill out the form and submit it:
        data = {
            "last_name": "test_with_resume",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "testing_email@netthandshome.care",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "944",
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": False,
            "availability_monday": False,
            "availability_tuesday": False,
            "availability_wednesday": False,
            "availability_thursday": False,
            "availability_friday": False,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        request = RequestFactory().post(reverse("web:employment_application_form"), data=data)

        view = EmploymentApplicationFormView()
        view.setup(request)

        # Verify the form returned errors:
        form = view.get_form()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(field="availability_monday"))
        self.assertFormError(form=form, field="availability_monday", errors="You must be available at least one day a week.")
        self.assertTrue(form.has_error(field="zipcode"))
        self.assertFormError(form=form, field="zipcode", errors="Enter a zip code in the format XXXXX or XXXXX-XXXX.")

        # Verify the new fruit was not created:
        self.assertFalse(EmploymentApplicationModel.objects.filter(home_address1=data.get("home_address1")).exists())

    def test_create_application_with_resume_submit_valid(self):

        test_file_good = SimpleUploadedFile(name="accepted_file.pdf", content=b"Accpeted File For Upload", content_type="application/pdf")
        # Fill out the form and submit it:
        data = {
            "last_name": "test_with_resume",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "testing_email@netthandshome.care",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": mock_zipcode,
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": False,
            "availability_monday": False,
            "availability_tuesday": True,
            "availability_wednesday": False,
            "availability_thursday": True,
            "availability_friday": False,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
            "resume_cv": test_file_good,
        }
        r = self.client.post(reverse("web:employment_application_form"), data=data)
        self.assertEqual(r.status_code, 302)

        # Verify the new submission  was created:
        application = EmploymentApplicationModel.objects.get(first_name=data.get("first_name"))
        self.assertEqual(str(application.state), str(data.get("state")))
        self.assertEqual(application.email, data.get("email"))
        self.assertIsNotNone(application.resume_cv)

    def test_create_application_with_resume_submit_invalid_file_type_vaild_extenstion(self):

        test_file_bad_content = SimpleUploadedFile(name="rejected_file.pdf", content=b"const file_output = 'output bad'  \n console.log(file_output)", content_type="text/javascript")
        # Fill out the form and submit it:
        data = {
            "last_name": "test_with_bad_resume",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "testing_email@netthandshome.care",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": mock_zipcode,
            "mobility": "C",
            "prior_experience": "J",
            "ipdh_registered": False,
            "availability_monday": False,
            "availability_tuesday": True,
            "availability_wednesday": False,
            "availability_thursday": True,
            "availability_friday": False,
            "availability_saturday": False,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
            "resume_cv": test_file_bad_content,
        }
        request = RequestFactory().post(reverse("web:employment_application_form"), data=data)

        view = EmploymentApplicationFormView()
        view.setup(request)

        # Verify the form returned errors:
        form = view.get_form()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(field="resume_cv"))
        self.assertFormError(form=form, field="resume_cv", errors="Invalid file type. Allowed types are .doc, .pdf, and .txt.")

        # Verify the new fruit was not created:
        self.assertFalse(EmploymentApplicationModel.objects.filter(last_name=data.get("last_name"), home_address1=data.get("home_address1")).exists())

    # def test_create_application_with_resume_submit_valid_file_type_invaild_size(self):
    #     """
    #     Verify the record is not created if invalid values are passed to the form:
    #     """
    #     test_file_bad_content = UploadedFile(file=BytesIO(b"I am a good file, but i am too large"), size=10028,  name="rejected_file.docx", content_type="application/msword")
    #     # Fill out the form and submit it:
    #     data = {
    #         "last_name": "test_with_bad_resume",
    #         "first_name": "new_employee",
    #         "contact_number": "+12023919919",
    #         "email": "testing_email@netthandshome.care",
    #         "home_address1": "1 North World Trade Tower",
    #         "home_address2": "15th Floor",
    #         "city": "Manhattan",
    #         "state": "NY",
    #         "zipcode": mock_zipcode,
    #         "mobility": "C",
    #         "prior_experience": "J",
    #         "ipdh_registered": False,
    #         "availability_monday": False,
    #         "availability_tuesday": True,
    #         "availability_wednesday": False,
    #         "availability_thursday": True,
    #         "availability_friday": False,
    #         "availability_saturday": False,
    #         "g-recaptcha-response": "PASSED",
    #         "captcha": "PASSED",
    #         "resume_cv": test_file_bad_content
    #     }
    #     print(test_file_bad_content.size)
    #     request = RequestFactory().post(reverse("web:employment_application_form"), data=data)

    #     view = EmploymentApplicationFormView()
    #     view.setup(request)

    #     # Verify the form returned errors:
    #     form = view.get_form()
    #     self.assertFalse(form.is_valid())
    #     self.assertTrue(form.has_error(field="resume_cv"))
    #     self.assertFormError(form=form, field="resume_cv", errors="Invalid file type. Allowed types are .doc, .pdf, and .txt.")

    #     # Verify the new fruit was not created:
    #     self.assertFalse(EmploymentApplicationModel.objects.filter(last_name=data.get("last_name"), home_address1=data.get("home_address1")).exists())


class TestClientServiceRequestFormView(TestCase):

    def test_create_client_service_request_client(self):
        # Verify the form loads:
        r = self.client.get(reverse("web:client_interest_form"))
        self.assertEqual(r.status_code, 200)

    def test_create_client_service_request_form_submit_client(self):

        # Fill out the form and submit it:
        data = {
            "last_name": "test",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "testing_email@netthandshome.care",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "21217",
            "insurance_carrier": "BCBS",
            "desired_service": "OT",
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        r = self.client.post(reverse("web:client_interest_form"), data=data)
        self.assertEqual(r.status_code, 301)

        # Verify the new fruit was created:
        application = ClientInterestSubmission.objects.get(email=data.get("email"))
        self.assertEqual(str(application.state), str(data.get("state")))
        self.assertEqual(application.email, data.get("email"))

    def test_create_client_service_request_form(self):
        """
        Verify the form loads with the correct data
        """
        # Verify the form loads:
        request = RequestFactory().get(reverse("web:client_interest_form"))
        view = ClientInterestFormView()
        view.setup(request)
        response = ClientInterestFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Verify the fields are on the form:
        form = view.get_form()
        self.assertIn("email", form.fields.keys())
        self.assertIn("contact_number", form.fields.keys())
        self.assertIn("first_name", form.fields.keys())
        self.assertIn("last_name", form.fields.keys())

    def test_create_client_service_request_submit_invalid(self):
        """
        Verify the record is not created if invalid values are passed to the form:
        """

        # Fill out the form and submit it:
        data = {
            "last_name": "tesdt",
            "first_name": "new_employee",
            "contact_number": "+12023919919",
            "email": "testing_email@netthandshome.care",
            "home_address1": "1 North World Trade Tower",
            "home_address2": "15th Floor",
            "city": "Manhattan",
            "state": "NY",
            "zipcode": "944",
            "insurance_carrier": "BCBS",
            "desired_service": True,
            "g-recaptcha-response": "PASSED",
            "captcha": "PASSED",
        }
        request = RequestFactory().post(reverse("web:client_interest_form"), data=data)

        view = ClientInterestFormView()
        view.setup(request)

        # Verify the form returned errors:
        form = view.get_form()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(field="desired_service"))
        self.assertTrue(form.has_error(field="zipcode"))

        # Verify the new fruit was not created:
        self.assertFalse(ClientInterestSubmission.objects.filter(home_address1=data.get("home_address1")).exists())
