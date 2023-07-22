from compliance.models import Contract
from crispy_forms.bootstrap import FormActions
from crispy_forms.bootstrap import Modal
from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Reset
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from employee.models import Employee


class EmployeeForm(forms.ModelForm):
    """Form definition for Employee Model."""

    contract_code = forms.ModelChoiceField(queryset=Contract.objects.all())

    class Meta:
        """Meta definition for EmployeeForm."""

        model = Employee
        fields = (
            "gender",
            "social_security",
            "middle_name",
            "street_address",
            "last_name",
            "first_name",
            "marital_status",
            "emergency_contact_first_name",
            "emergency_contact_last_name",
            "emergency_contact_relationship",
            "emergency_contact_phone",
            "city",
            "email",
            "phone",
            "state",
            "zipcode",
            "ethnicity",
            "family_hca",
            "language",
            "cpr_verification",
            "qualifications",
            "race",
            "qualifications_verification",
            "username",
            "date_of_birth",
        )
        labels = {
            "language": _(
                "Language Preference",
            ),
            "family_hca": _("Check if patient is related by blood or marriage"),
            "qualifications": _(
                "Highest Level of Education/Home Healthcare Qualification",
            ),
            "qualifications_verification": _("Upload Degree, GED or Diploma"),
            "cpr_verification": _("CPR Card"),
            "hhs_oig_exclusionary_check_verification": _(
                "Upload Fingerprinting Results",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("profile")
        self.helper.form_id = "profile"
        self.helper.form_method = "post"
        self.helper.form
        self.fields["date_of_birth"].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.helper.layout = Layout(
            HTML(
                """
        <h6 class="small-heading muted-text mb-4">User Information</strong></h6>
        <div class="pl-lg-4">
        """,
            ),
            Row(
                UneditableField("username", css_class="form-group col-6 mb-0 "),
                Column(
                    "email",
                    css_class="form-group col-6 mb-0  editable",
                ),
                css_class="form-row ",
            ),
            Row(
                Column(
                    "first_name",
                    readonly=True,
                    css_class="form-group col-md-4 mb-0  editable",
                ),
                Column(
                    "middle_name",
                    readonly=True,
                    css_class="form-group col-md-4 mb-0  editable",
                ),
                Column(
                    "last_name",
                    readonly=True,
                    css_class="form-group col-md-44 mb-0  editable",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "language",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0",
                ),
                Column(
                    "ethnicity",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0",
                ),
                Column(
                    "race",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0",
                ),
                css_class="form-row ",
            ),
            Row(
                Column("family_hca", css_class="form-group col-md-4 mb-0"),
                Column("qualifications", css_class="form-group col-md-4 mb-0"),
                Column("date_of_birth", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            HTML("""</div> """),
            HTML("""<hr class="my-4 />"""),
            HTML(
                """
        <h6 class="small-heading muted-text mb-4">Contact Information</strong></h6>
        <div class="pl-lg-4">

        """,
            ),
            Row(
                Column(
                    "street_address",
                    readonly=True,
                    css_class="form-group col-md-12 mb-0 editable   ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "city",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "state",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "zipcode",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "phone",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "social_security",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "gender",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            HTML("""</div> """),
            HTML("""<hr class="my-4 />"""),
            HTML(
                """
        <h6 class="small-heading muted-text mb-4">Emergency Contact</strong></h6>
        <div class="pl-lg-4">

        """,
            ),
            Row(
                Column(
                    "emergency_contact_first_name",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "emergency_contact_last_name",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "emergency_contact_phone",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "emergency_contact_relationship",
                    readonly=True,
                    css_class="form-group col-lg-12 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            HTML("""<hr class="my-4 />"""),
            HTML(
                """
        <h6 class="small-heading muted-text mb-4">Supporting Documentation</strong></h6>
        <div class="pl-lg-4">

        """,
            ),
            Row(
                Column(
                    "cpr_verification",
                    readonly=True,
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                Column(
                    "qualifications_verification",
                    help_text="Please upload a copy of the document selected in the User Information field - Highest Level of Education/Home Healthcare Qualification",
                    css_class="form-group col-lg-4 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                FormActions(
                    Submit("save", "Save changes", id="edit-button"),
                    Reset(
                        "cancel",
                        "Cancel",
                        css_class="btn btn-danger",
                        id="cancel-edits-btn",
                    ),
                ),
                css_class="form-row",
            ),
        )
