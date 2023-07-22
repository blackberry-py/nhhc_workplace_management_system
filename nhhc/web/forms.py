from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Row, Field
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from web.models import ClientInterestSubmissions
from web.models import EmploymentApplicationModel
from captcha.fields import ReCaptchaField


class ClientInterestForm(forms.ModelForm):
    """Form definition for ClientInterestSubmission."""

    captcha = ReCaptchaField()

    class Meta:
        """Meta definition for ClientInterestSubmissionform."""

        model = ClientInterestSubmissions
        fields = (
            "first_name",
            "last_name",
            "contact_number",
            "email",
            "zipcode",
            "insurance_carrier",
            "desired_service",
            "captcha",
        )


class EmploymentApplicationForm(forms.ModelForm):
    """Form definition for EmploymentApplicationModel."""

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
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
            "home_address",
            Row(
                Column("city", css_class="form-group col-md-6 mb-0"),
                Column("state", css_class="form-group col-md-4 mb-0"),
                Column("zipcode", css_class="form-group col-md-2 mb-0"),
                css_class="form-row ",
            ),
            HTML("""<h3 class="application-text">Relevant Experience</h3>"""),
            Row(
                Column("mobility", css_class="form-group col-md-6 mb-0"),
                Column("prior_experience", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("ipdh_registered", css_class="form-group col-md-12 mb-0"),
                css_class="form-row",
            ),
            HTML("""<h3 class="application-text">Work Availability</h3>"""),
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
                Column("availability_sunday", css_class="form-group col-md- mb-0"),
                css_class="form-row",
            ),
            Field("captcha", placeholder="Enter captcha"),
            Submit("submit", "Submit Application"),
        )

    class Meta:
        """Meta definition for EmploymentApplicationModelForm."""

        model = EmploymentApplicationModel
        fields = (
            "first_name",
            "last_name",
            "contact_number",
            "email",
            "home_address",
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
        }
