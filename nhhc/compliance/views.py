"""
Module: nhhc.compliance.views

This module contains views related to compliance and contract management within the application. It includes views for creating contracts, managing compliance profiles, and generating reports.

Classes:
- CreateContractFormView: A FormView for creating new contracts using the ContractForm.
- ComplianceProfileDetailView: A DetailView for displaying compliance details for an employee.
- ComplianceProfileFormView: An UpdateView for managing compliance forms for an employee.
- ComplianceProfile: A View for handling GET and POST requests related to compliance profiles.

Functions:
- create_contract: Placeholder function for creating contracts.
- generate_report: Function for generating a CSV report with employee data.

Note: This module interacts with models from the compliance app and uses form classes for data input and display.
"""


from compliance.forms import ComplianceForm, ContractForm
from compliance.models import Compliance
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from formset.upload import FileUploadMixin

# Create your views here.


def create_contract(request):
    pass


class CreateContractFormView(FormView):
    """
    class-based template rendering view for creating a new contract form.

    Attributes:
    - template_name: a string representing the template file to render the form
    - form_class: the form class to use for creating the contract form
    """

    template_name = "new_contract.html"
    form_class = ContractForm


class ComplianceProfileDetailView(DetailView):
    """
    This class is a DetailView that displays the details of a Compliance object.
    """

    model = Compliance
    template_name = "compliance_details.html"
    context_object_name = "employee"

    def get_object(self) -> Compliance:
        """
        This method retrieves the Compliance object for the current user.

        Returns:
        Compliance object: The Compliance object for the current user.
        """
        return Compliance.objects.get(employee=self.request.user)


class ComplianceProfileFormView(UpdateView, FileUploadMixin):
    """
    This class is a view for updating compliance profiles.

    Attributes:
    - form_class: The form class to be used for updating compliance profiles.
    - model: The model to be used for updating compliance profiles.
    - template_name: The template to be rendered for the compliance form.
    - context_object_name: The context object name to be used in the template.
    """

    form_class = ComplianceForm
    model = Compliance
    template_name = "compliance_forms.html"
    context_object_name = "employee"


# TODO: Implement Reporting
def generate_report(requst):
    raise NotImplementedError
    # sessio÷≥nDataCSV = f"TTPUpload{now.to_date_string()}.csv"
    # sessions = employee_report_export()
    # with open(sessionDataCSV, "w+") as csv_output_file_pointer:
    #     csv_writer = csv.writer(csv_output_file_pointer)
    #     # Writing headers of CSV file
    #     header = (
    #         "SSN",
    #         "FirstName",
    #         "LastName",
    #         "MiddleName",
    #         "DateOfBirth",
    #         "Gender",
    #         "EmailAddress",
    #         "Ethnicity",
    #         "Race",
    #         "Qualifications",
    #         "LanguageCode",
    #         "ContractNumber",
    #         "EmployeeTitle",
    #         "TitleStartDate",
    #         "CaseLoad",
    #         "Prior to 10/01/2021",
    #         "TrainingDate",
    #         "InitialCBC",
    #         "MostCurrentCBC",
    #     )
    #     csv_writer.writerow(header)
    #     for employee in employees:
    #         row_data = (
    #             employee["social_security"],
    #             employee["first_name"],
    #             employee["last_name"],
    #             employee["middle_name"],
    #             employee["date_of_birth"],
    #             employee["gender"],
    #             employee["ethnicity"],
    #             employee["race"],
    #             employee["qualifications"],
    #             employee["language"],
    #             employee["contract"],
    #             employee["title"],
    #             employee["hire_date"],
    #             "Find Out What Caseload Is" "False",
    #             " ",
    #             employee["initial_idph_background_check_completion_date"],
    #             employee["current_idph_background_check_completion_date"],
    #         )
    #         csv_writer.writerow(row_data)
    #         os.open(sessionDataCSV, os.O_NONBLOCK)
