from compliance.models import Compliance
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


class ContractForm(forms.ModelForm):
    """Form definition for Employee Model."""

    class Meta:
        """Meta definition for EmployeeForm."""

        model = Contract
        fields = "__all__"


class ComplianceForm(forms.ModelForm):
    class Meta:
        model = Compliance
        fields = (
            "aps_check_passed",
            "aps_check_verification",
            "hhs_oig_exclusionary_check_verification",
            "hhs_oig_exclusionary_check_completed",
            "idph_background_check_completed",
            "idph_background_check_verification",
            "initial_idph_background_check_completion_date",
            "current_idph_background_check_completion_date",
            "training_exempt",
            "pre_training_verification",
            "pre_service_completion_date",
            "added_to_TTP_portal",
            "contract_code",
            "job_title",
        )

        labels = {
            "pre_training_verification": _("24 Hour Pre-Training Certificate"),
            "hhs_oig_exclusionary_check_verification": _(
                "Upload Fingerprinting Results",
            ),
            "hhs_oig_exclusionary_check_completed": _("Fingerprinting Completed?"),
            "training_exempt": _("Is This Employee Exempt From Training Requirement?"),
            "pre_service_completion_date": _("24-Hour Pre-Service Completiom Date"),
            "initial_idph_background_check_completion_date": _(
                "Initial IDPH Background Check Result Date",
            ),
            "current_idph_background_check_completion_date": _(
                "Most Recent IDPH Background Check Result Date",
            ),
            "contract_code": _("Contract"),
            "added_to_TTP_portal": _("Added to TTP?"),
            "aps_check_verification": _("APS Work Eligibility Verification"),
            "aps_check_passed": _("APS Work Eligibility Checked?"),
            "idph_background_check_completed": _("IDPH Background Check"),
            "idph_background_check_verification": _(
                "Upload Most Recent Background Check",
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "/employee"
        self.helper.form_id = "profile"
        self.helper.form_method = "post"
        self.fields[
            "initial_idph_background_check_completion_date"
        ].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.fields[
            "current_idph_background_check_completion_date"
        ].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.fields["pre_service_completion_date"].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.helper.layout = Layout(
            HTML(
                """
        <h2 class="small-heading muted-text mb-4">Staff Use Only</strong></h2>

        """,
            ),
            Row(
                Column(
                    "job_title",
                    readonly=True,
                    css_class="form-group col-12 mb-0 editable ",
                ),
            ),
            Row(
                Column(
                    "hhs_oig_exclusionary_check_completed",
                    readonly=True,
                    css_class="form-group col-4 mb-0 editable ",
                ),
                Column(
                    "hhs_oig_exclusionary_check_verification",
                    css_class="form-group col-8 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "contract_code",
                    readonly=True,
                    css_class="form-group col-4 mb-0 editable ",
                ),
                Column(
                    "training_exempt",
                    css_class="form-group col-4 mb-0 editable ",
                ),
                Column(
                    "added_to_TTP_portal",
                    css_class="form-group col-4 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "aps_check_passed",
                    readonly=True,
                    css_class="form-group col-6 mb-0 editable ",
                ),
                Column(
                    "aps_check_verification",
                    readonly=True,
                    css_class="form-group col-6 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "idph_background_check_completed",
                    readonly=True,
                    css_class="form-group col-12 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "initial_idph_background_check_completion_date",
                    readonly=True,
                    css_class="form-group col-6 mb-0 editable ",
                ),
                Column(
                    "current_idph_background_check_completion_date",
                    css_class="form-group col-6 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "idph_background_check_verification",
                    readonly=True,
                    css_class="form-group col-12 mb-0 editable ",
                ),
                css_class="form-row",
            ),
            Row(
                Column(
                    "pre_service_completion_date",
                    readonly=True,
                    css_class="form-group col-6 mb-0 editable ",
                ),
                Column(
                    "pre_training_verification",
                    css_class="form-group col-6 mb-0 editable ",
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
