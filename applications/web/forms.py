"""
Module: Form Module
Description: This module contains the form definitions for the ClientInterestForm and EmploymentApplicationForm.

ClientInterestForm:
- This form is used for capturing client interest submissions.
- It includes fields for first name, last name, contact number, email, zipcode, insurance carrier, desired service, and captcha.

EmploymentApplicationForm:
- This form is used for capturing employment applications.
- It includes fields for basic information, relevant experience, work availability, and captcha.

Both forms utilize the ReCaptchaField for added security.

"""

from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, Submit
from django import forms
from django.forms import ModelForm, fields
from django.utils.translation import gettext_lazy as _
from formset.fields import Activator
from formset.renderers import ButtonVariant
from formset.widgets import Button, UploadedFileInput

from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel


class ClientInterestForm(ModelForm):
    """Form definition for ClientInterestSubmission."""

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"autocomplete": "off", "form_id": "employment-application"}
        self.fields["captcha"].label = False

        self.helper.layout = Layout(
            HTML("""<h3 class="application-text">Patient Information</h3>"""),
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("contact_number", css_class="form-group col-md-6 mb-0"),
                Column("email", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("home_address1", css_class="form-group col-8"),
                Column("home_address2", css_class="form-group col-4"),
                css_class="form-row",
            ),
            Row(
                Column("city", css_class="form-group col-md-6 mb-0"),
                Column("state", css_class="form-group col-md-4 mb-0"),
                Column("zipcode", css_class="form-group col-md-2 mb-0"),
                css_class="form-row ",
            ),
            HTML("""<h3 class="application-text">Service Information</h3>"""),
            Row(
                Column("insurance_carrier", css_class="form-group col-md-6 mb-0"),
                Column("desired_service", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Field("captcha", placeholder="Enter captcha"),
            HTML(
                """ <button id="loading-btn-submit" class="btn btn-primary" style="display: none;" disabled>
          <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
          Submitting...
        </button> """
            ),
            Submit("submit", "Submit Interest", css_id="btn-submit"),
        )

    class Meta:
        """Meta definition for ClientInterestSubmissionform."""

        model = ClientInterestSubmission
        fields = (
            "first_name",
            "last_name",
            "contact_number",
            "home_address1",
            "home_address2",
            "city",
            "zipcode",
            "state",
            "email",
            "zipcode",
            "insurance_carrier",
            "desired_service",
            "captcha",
        )
        labels = {
            "home_address2": _("Unit/Apartment"),
            "home_address1": _("Street Address"),
        }


class EmploymentApplicationForm(ModelForm):
    """Form definition for EmploymentApplicationModel."""

    submit = Activator(
        widget=Button(
            action="disable -> spinner -> delay(500) -> submit -> reload !~ scrollToError",
            button_variant=ButtonVariant.SUCCESS,
            auto_disable=True,
            attrs={"value": "Apply"},
        ),
    )
    captcha = ReCaptchaField()
    resume_cv = fields.FileField(
        label="Resumé/Work History",
        widget=UploadedFileInput(
            attrs={
                "max-size": 1024 * 1024,
                "accept": "application/msword, application/pdf, text/plain",
            }
        ),
        help_text="Optional - Upload a copy of your resume or work history. Only .doc, .pdf OR .txt up to 1MB",
        required=False,
    )

    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"autocomplete": "off", "enctype": "multipart/form-data"}
        self.fields["captcha"].label = False

        self.helper.layout = Layout(
            HTML(
                """
        <h3 class="application-text">Basic Information</strong></h3>""",
            ),
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-0"),
                Column("last_name", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("contact_number", css_class="form-group col-md-6 mb-0"),
                Column("email", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("home_address1", css_class="form-group col-8"),
                Column("home_address2", css_class="form-group col-4"),
                css_class="form-row",
            ),
            Row(
                Column("city", css_class="form-group col-md-6 mb-0"),
                Column("state", css_class="form-group col-md-4 mb-0"),
                Column("zipcode", css_class="form-group col-md-2 mb-0"),
                css_class="form-row ",
            ),
            HTML(
                """<h3 class="application-text">Relevant Experience</h3>""",
            ),
            Row(
                Column("mobility", css_class="form-group col-md-6 mb-0"),
                Column("prior_experience", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("ipdh_registered", css_class="form-group col-md-12 mb-0"),
                css_class="form-row",
            ),
            HTML(
                """<h3 class="application-text">Work Availability</h3>""",
            ),
            Row(
                Column("availability_monday", css_class="form-group col-md-3 mb-0"),
                Column("availability_tuesday", css_class="form-group col-md-3 mb-0"),
                Column("availability_wednesday", css_class="form-group col-md-3 mb-0"),
                Column("availability_thursday", css_class="form-group col-md-3 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("availability_friday", css_class="form-group col-md-3 mb-0"),
                Column("availability_saturday", css_class="form-group col-md-3 mb-0"),
                Column("availability_sunday", css_class="form-group col-md-3 mb-0"),
                css_class="form-row",
            ),
            HTML(
                """<h3 class="application-text">Supporting Documents</h3>""",
            ),
            Row(Column("resume_cv", css_class="form-group col-md-12 mb-0"), css_class="form-row"),
            Field("captcha", placeholder="Enter captcha"),
            HTML(
                """ <button id="loading-btn-submit" class="btn btn-primary" style="display: none;" disabled>
          <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
          Submitting...
        </button> """
            ),
            Submit(name="submit", value="Apply!", css_id="btn-submit"),
        )

    def clean(self):
        super().clean()

        # Validate availability
        availability_fields = [
            "availability_sunday",
            "availability_monday",
            "availability_tuesday",
            "availability_wednesday",
            "availability_thursday",
            "availability_friday",
            "availability_saturday",
        ]
        availability_data = [self.cleaned_data.get(day) for day in availability_fields]

        if not any(availability_data):
            error = forms.ValidationError(
                _("You must be available at least one day a week."),
                code="invalid",
            )
            for field in availability_fields:
                self.add_error(field, error)

        if resume_cv := self.cleaned_data.get("resume_cv"):
            # Validate file size
            max_size = 2 * 1024 * 1024  # 2 MB
            if resume_cv.size > max_size:
                self.add_error(
                    "resume_cv",
                    forms.ValidationError(
                        _("File size must not exceed 1MB."),
                        code="file_too_large",
                    ),
                )

            # Validate MIME type
            allowed_mime_types = [
                "application/msword",
                "application/pdf",
                "text/plain",
            ]
            if resume_cv.content_type not in allowed_mime_types:
                self.add_error(
                    "resume_cv",
                    forms.ValidationError(
                        _("Invalid file type. Allowed types are .doc, .pdf, and .txt."),
                        code="invalid_mime_type",
                    ),
                )

    class Meta:
        """Meta definition for EmploymentApplicationModelForm."""

        model = EmploymentApplicationModel
        fields = (
            "first_name",
            "last_name",
            "contact_number",
            "email",
            "home_address1",
            "home_address2",
            "city",
            "state",
            "zipcode",
            "mobility",
            "ipdh_registered",
            "prior_experience",
            "availability_monday",
            "availability_tuesday",
            "availability_wednesday",
            "availability_thursday",
            "availability_friday",
            "availability_saturday",
            "availability_sunday",
            "resume_cv",
            "captcha",
        )
        labels = {
            "ipdh_registered": _(
                "Currently Registered With the IPDH Health Care Worker Registry",
            ),
            "availability_monday": _("Monday"),
            "availability_tuesday": _("Tuesday"),
            "availability_wednesday": _("Wednesday"),
            "availability_thursday": _("Thursday"),
            "availability_friday": _("Friday"),
            "availability_saturday": _("Saturday"),
            "availability_sunday": _("Sunday"),
            "home_address2": _("Unit/Apartment"),
            "home_address1": _("Street Address"),
        }
