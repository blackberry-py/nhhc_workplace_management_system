from compliance.models import Contract
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Reset, Row, Submit
from django.forms import ModelChoiceField, ModelForm, fields, forms
from django.forms.widgets import DateInput
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from employee.models import Employee
from formset.views import FormView
from formset.widgets import UploadedFileInput


class EmployeeForm(ModelForm):
    """Form definition for Employee Model."""

    class Meta:
        """Meta definition for EmployeeForm."""

        model = Employee
        # fields = (
        #     "employee_id",
        #     "gender",
        #     "social_security",
        #     "middle_name",
        #     "street_address1",
        #     "street_address2",
        #     "last_name",
        #     "first_name",
        #     "marital_status",
        #     "emergency_contact_first_name",
        #     "emergency_contact_last_name",
        #     "emergency_contact_relationship",
        #     "emergency_contact_phone",
        #     "city",
        #     "email",
        #     "phone",
        #     "state",
        #     "zipcode",
        #     "ethnicity",
        #     "family_hca",
        #     "language",
        #     "cpr_verification",
        #     "qualifications",
        #     "race",
        #     "qualifications_verification",
        #     "username",
        #     "date_of_birth",
        # )
        fields = "__all__"
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
            "hhs_oig_exclusionary_check_verification": _("Upload Fingerprinting Results"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("profile")
        self.helper.form_id = "profile"
        self.helper.form_method = "post"
        self.helper.form
        self.fields["date_of_birth"].widget = DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.helper.layout = Layout(
            HTML(
                """
        <h3 class="small-heading muted-text mb-4">Employee Information</strong></h3>
        <div class="pl-lg-4">
        """,
            ),
            Row(
                Column(Field("username", css_class="", readonly=True), css_class="form-group col-4 mb-0"),
                Column(
                    HTML(
                        """<div class="row">
                 <div class="form-group col-4 mb-0">
                 <label class="form-label">Employee ID Number</label>
                 </div>
                 <div class="col-6">
                 <h5 class="textinput form-control" readonly>{{ employee.employee_id }}</h5>
                 </div>
                 </div> """
                    ),
                    css_class="form-group col-4 mb-0",
                ),
                Column(
                    "email",
                    css_class="form-group col-4 mb-0  editable",
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
                    css_class="form-group col-md-4 mb-0  editable",
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
        <h3 class="small-heading muted-text mb-4">Contact Information</strong></h3>
        <div class="pl-lg-4">

        """,
            ),
            Row(
                Column(
                    "street_address1",
                    readonly=True,
                    css_class="form-group col-md-8 mb-0 editable   ",
                ),
                Column(
                    "street_address2",
                    readonly=True,
                    css_class="form-group col-md-4 mb-0 editable",
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
        <h3 class="small-heading muted-text mb-4">Emergency Contact</strong></h3>
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
        <h3 class="small-heading muted-text mb-4">Supporting Documentation</strong></h3>
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
