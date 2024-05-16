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


from typing import Any
from compliance.forms import ComplianceForm, ContractForm
from compliance.models import Compliance
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import TemplateView
from formset.upload import FileUploadMixin
from employee.models import Employee
import json
from django.views.decorators.http import require_POST
from compliance.tasks import process_signed_form
from django.http import HttpRequest, HttpResponse
from rest_framework import status
from loguru import logger

# Create your views here.


# SECTION - Contract Related Viewws
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

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     """
    #     Retrieves the context data for the view.

    #     Parameters:
    #     - kwargs (Any): Additional keyword arguments.

    #     Returns:
    #     - dict[str, Any]: The context data for the view.
    #     """
    #     context = super().get_context_data(**kwargs)
    #     context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
    #     return context


# !SECTION
# SECTION - Compliance Related Views
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


# !SECTION

# SECTION - Attestation Forms


@require_POST
def signed_attestations(request: HttpRequest) -> HttpResponse:
    docuseal_payload = json.loads(request.POST)
    uploaded = process_signed_form(docuseal_payload)
    try:
        if uploaded:
            return HttpResponse(content="Posted To S3", status=status.HTTP_201_CREATED)
        else:
            logger.trace()
            return HttpResponse(content="Failed To Posted To S3", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        logger.error(f"Error Uploding to S3: {e}")


class DocusealCompliaceDocsSigning_IDOA(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/r5UbQeVsQgkwUp"
        return context


class DocusealCompliaceDocsSigning_HCA(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/3KA4PP4CEjpy4r"
        return context


class DocusealCompliaceDocsSigning_DoNotDrive(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/v1FPgz9xgBJVgH"
        return context


class DocusealCompliaceDocsSigning_JobDesc(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/KQUEkomQZr1ddD"
        return context


class DocusealCompliaceDocsSigning_i9(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/ovQk6ACHqajQvC"
        return context


class DocusealCompliaceDocsSigning_irs_w4(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "hhttps://docuseal.co/d/wmJGUH3wU2GrUJ"
        return context


# !SECTION


# TODO: Implement Reporting
def generate_report(request):
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
