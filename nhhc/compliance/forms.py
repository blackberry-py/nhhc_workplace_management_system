from datetime import datetime

from compliance.models import Compliance, Contract
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Layout, Reset, Row, Submit
from django import forms
from django.utils.translation import gettext_lazy as _


class ContractForm(forms.ModelForm):
    """
    Form definition for Contract Model.

    This form is used to create and update contract information.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "contract"
        self.helper.form_method = "post"
        self.fields["contract_year_end"].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.fields["contract_year_end"].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )

    def is_active_contract(self, contract_year_start, contract_year_end):
        """
        Check if the contract is currently active based on the contract year start and end dates.

        Args:
            contract_year_start (datetime): The start date of the contract year.
            contract_year_end (datetime): The end date of the contract year.

        Returns:
            bool: True if the contract is active, False otherwise.
        """

    def save(self, commit=True):
        """
        Save the form data to the Contract model instance.

        Args:
            commit (bool, optional): Whether to save the instance to the database. Defaults to True.

        Returns:
            Contract: The saved Contract instance.
        """
        form_data = self.cleaned_data
        self.instance.code = form_data["code"]
        self.instance.name = form_data["name"]
        self.instance.description = form_data["description"]
        self.instance.contract_year_start = form_data["contract_year_start"]
        self.instance.contract_year_end = form_data["contract_year_end"]
        self.instance.active = self.is_active_contract(form_data["contract_year_start"], form_data["contract_year_end"])
        return super(ContractForm, self).save(commit)

    class Meta:
        model = Contract
        fields = (
            "code",
            "name",
            "description",
            "contract_year_start",
            "contract_year_end",
        )


class ComplianceForm(forms.ModelForm):
    """
    Form definition for Compliance Model.

    This form is used to manage compliance-related information for employees.
    """

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
        self.fields["initial_idph_background_check_completion_date"].widget = forms.widgets.DateInput(
            attrs={"type": "date", "class": "form-control"},
        )
        self.fields["current_idph_background_check_completion_date"].widget = forms.widgets.DateInput(
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
                    HTML(
                        """ <button id="loading-btn-submit" class="btn btn-primary" style="display: none;" disabled>
          <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
          Saving...
        </button> """
                    ),
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
